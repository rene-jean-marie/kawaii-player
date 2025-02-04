"""
Example AniList plugin for Kawaii Player
"""
import json
import logging
from typing import Optional, Dict, List
from PyQt5 import QtCore

from kawaii_player import NetworkManager, PlaylistManager, SettingsManager

logger = logging.getLogger(__name__)

class AniListPlugin(QtCore.QObject):
    """Plugin for AniList integration"""
    
    # Signals
    search_completed = QtCore.pyqtSignal(list)  # search results
    media_loaded = QtCore.pyqtSignal(dict)  # media info
    list_updated = QtCore.pyqtSignal(str, str)  # status, title
    
    def __init__(
        self,
        network: NetworkManager,
        playlist: PlaylistManager,
        settings: SettingsManager
    ):
        super().__init__()
        self.network = network
        self.playlist = playlist
        self.settings = settings
        
        # API endpoint
        self.api_url = 'https://graphql.anilist.co'
        
        # Get API token from settings
        self.access_token = settings.get('plugins.anilist.access_token', '')
    
    async def search_anime(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20
    ) -> List[Dict]:
        """Search for anime"""
        try:
            # GraphQL query
            gql_query = """
            query ($search: String, $page: Int, $perPage: Int) {
                Page(page: $page, perPage: $perPage) {
                    media(search: $search, type: ANIME) {
                        id
                        title {
                            romaji
                            english
                            native
                        }
                        description
                        coverImage {
                            large
                        }
                        bannerImage
                        episodes
                        duration
                        status
                        season
                        seasonYear
                        averageScore
                        genres
                        studios {
                            nodes {
                                name
                            }
                        }
                    }
                }
            }
            """
            
            variables = {
                'search': query,
                'page': page,
                'perPage': per_page
            }
            
            # Make request
            response = await self.network.request(
                self.api_url,
                method='POST',
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    'query': gql_query,
                    'variables': variables
                })
            )
            
            data = json.loads(response)
            
            # Format results
            results = []
            for item in data['data']['Page']['media']:
                result = {
                    'id': item['id'],
                    'title': {
                        'romaji': item['title']['romaji'],
                        'english': item['title']['english'],
                        'native': item['title']['native']
                    },
                    'description': item['description'],
                    'cover_image': item['coverImage']['large'],
                    'banner_image': item['bannerImage'],
                    'episodes': item['episodes'],
                    'duration': item['duration'],
                    'status': item['status'],
                    'season': item['season'],
                    'year': item['seasonYear'],
                    'score': item['averageScore'],
                    'genres': item['genres'],
                    'studios': [
                        studio['name']
                        for studio in item['studios']['nodes']
                    ]
                }
                results.append(result)
            
            self.search_completed.emit(results)
            return results
            
        except Exception as e:
            logger.error(f'AniList search failed: {str(e)}')
            return []
    
    async def get_anime_details(self, anime_id: int) -> Optional[Dict]:
        """Get detailed anime information"""
        try:
            # GraphQL query
            gql_query = """
            query ($id: Int) {
                Media(id: $id, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    description
                    coverImage {
                        large
                    }
                    bannerImage
                    episodes
                    duration
                    status
                    season
                    seasonYear
                    averageScore
                    genres
                    studios {
                        nodes {
                            name
                        }
                    }
                    streamingEpisodes {
                        title
                        thumbnail
                        url
                        site
                    }
                    relations {
                        edges {
                            relationType
                            node {
                                id
                                title {
                                    romaji
                                }
                                type
                            }
                        }
                    }
                    recommendations {
                        nodes {
                            mediaRecommendation {
                                id
                                title {
                                    romaji
                                }
                                coverImage {
                                    large
                                }
                            }
                        }
                    }
                }
            }
            """
            
            variables = {'id': anime_id}
            
            # Make request
            response = await self.network.request(
                self.api_url,
                method='POST',
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    'query': gql_query,
                    'variables': variables
                })
            )
            
            data = json.loads(response)
            media = data['data']['Media']
            
            # Format result
            result = {
                'id': media['id'],
                'title': {
                    'romaji': media['title']['romaji'],
                    'english': media['title']['english'],
                    'native': media['title']['native']
                },
                'description': media['description'],
                'cover_image': media['coverImage']['large'],
                'banner_image': media['bannerImage'],
                'episodes': media['episodes'],
                'duration': media['duration'],
                'status': media['status'],
                'season': media['season'],
                'year': media['seasonYear'],
                'score': media['averageScore'],
                'genres': media['genres'],
                'studios': [
                    studio['name']
                    for studio in media['studios']['nodes']
                ],
                'streaming_episodes': media['streamingEpisodes'],
                'relations': [
                    {
                        'type': edge['relationType'],
                        'id': edge['node']['id'],
                        'title': edge['node']['title']['romaji'],
                        'media_type': edge['node']['type']
                    }
                    for edge in media['relations']['edges']
                ],
                'recommendations': [
                    {
                        'id': rec['mediaRecommendation']['id'],
                        'title': rec['mediaRecommendation']['title']['romaji'],
                        'cover_image': rec['mediaRecommendation']['coverImage']['large']
                    }
                    for rec in media['recommendations']['nodes']
                ]
            }
            
            self.media_loaded.emit(result)
            return result
            
        except Exception as e:
            logger.error(f'Failed to get anime details: {str(e)}')
            return None
    
    async def update_list(
        self,
        media_id: int,
        status: str,
        progress: Optional[int] = None
    ) -> bool:
        """Update anime list entry"""
        if not self.access_token:
            logger.error('AniList access token not set')
            return False
            
        try:
            # GraphQL mutation
            gql_mutation = """
            mutation (
                $mediaId: Int,
                $status: MediaListStatus,
                $progress: Int
            ) {
                SaveMediaListEntry(
                    mediaId: $mediaId,
                    status: $status,
                    progress: $progress
                ) {
                    id
                    status
                    progress
                    media {
                        title {
                            romaji
                        }
                    }
                }
            }
            """
            
            variables = {
                'mediaId': media_id,
                'status': status.upper(),
                'progress': progress
            }
            
            # Make request
            response = await self.network.request(
                self.api_url,
                method='POST',
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'query': gql_mutation,
                    'variables': variables
                })
            )
            
            data = json.loads(response)
            entry = data['data']['SaveMediaListEntry']
            
            self.list_updated.emit(
                entry['status'],
                entry['media']['title']['romaji']
            )
            return True
            
        except Exception as e:
            logger.error(f'Failed to update list: {str(e)}')
            return False
    
    def add_to_playlist(
        self,
        media_info: Dict,
        playlist_name: Optional[str] = None
    ) -> bool:
        """Add streaming episodes to playlist"""
        try:
            # Create playlist if needed
            if playlist_name is None:
                playlist_name = media_info['title']['romaji']
                self.playlist.create_playlist(playlist_name)
            
            # Add streaming episodes
            for episode in media_info['streaming_episodes']:
                self.playlist.add_item(
                    title=episode['title'],
                    url=episode['url'],
                    thumbnail=episode['thumbnail'],
                    playlist_name=playlist_name,
                    metadata={
                        'source': 'anilist',
                        'site': episode['site'],
                        'anime_id': media_info['id']
                    }
                )
            
            return True
            
        except Exception as e:
            logger.error(f'Failed to add to playlist: {str(e)}')
            return False
    
    def get_season_chart(
        self,
        year: Optional[int] = None,
        season: Optional[str] = None
    ) -> List[Dict]:
        """Get seasonal anime chart"""
        pass  # TODO: Implement seasonal chart
    
    def get_recommendations(
        self,
        media_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Get personalized recommendations"""
        pass  # TODO: Implement recommendations
    
    def get_airing_schedule(
        self,
        media_ids: List[int]
    ) -> List[Dict]:
        """Get airing schedule for anime"""
        pass  # TODO: Implement airing schedule
