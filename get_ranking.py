# -*- coding: utf-8 -*-
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# These are IDs from the YouTube urls of evermore lyric videos.
# Change to whatever album/videos you want to.
NAMES_TO_ID = {
    'willow': '7EvwIw4gIyk', # Note: this is the lyric video, not music video id
    'champagne problems': 'wMpqCRF7TKg',
    'gold rush': 'Pz-f9mM3Ms8',
    'tis the damn season': 'WuvhOD-mP8M',
    'tolerate it': 'ukxEKY_7MOc',
    'no body, no crime': 'IEPomqor2A8',
    'happiness': 'tP4TTgt4nb0',
    'dorothea': 'zI4DS5GmQWE',
    'coney island': 'c_p_TBaHvos',
    'ivy': '9nIOx-ezlzA',
    'cowboy like me': 'YPlNBb6I8qU',
    'long story short': 'rqQHa2HcGtM',
    'marjorie': 'hP6QpMeSG6s',
    'closure': 'AIFnKqIeEdY',
    'evermore': 'EXLgZZE072g',
    'willow (music video)': 'RsEZmictANA'
}

def print_ranking():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json" # TODO: rename to your secret file name

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    song_to_stats = {} # Map each song name to its raw statistics
    for name, video_id in NAMES_TO_ID.items():
        request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        response = request.execute()
        statistics = response['items'][0]['statistics']
        views = int(statistics['viewCount'])
        likes = int(statistics['likeCount'])
        dislikes = int(statistics['dislikeCount'])
        song_to_stats[name] = [likes / (likes + dislikes), likes / views, views]
    
    all_stats = song_to_stats.values()

    # Min and max likes to reactions ratio
    min_lr = min(stat[0] for stat in all_stats)
    max_lr = max(stat[0] for stat in all_stats)

    # Min and max likes to views ratio
    min_lv = min(stat[1] for stat in all_stats)
    max_lv = max(stat[1] for stat in all_stats)

    # Min and max views
    min_views = min(stat[2] for stat in all_stats)
    max_views = max(stat[2] for stat in all_stats)
    
    song_to_scores = {} # Map each song name to its normalized scores
    for name, stat in song_to_stats.items():
        lr_score = (stat[0] - min_lr) / (max_lr - min_lr)
        lv_score = (stat[1] - min_lv) / (max_lv - min_lv)
        views_score = (stat[2] - min_views) / (max_views - min_views)
        song_to_scores[name] = \
            [lr_score, lv_score, views_score]
    
    # Sort songs by the sum of the the three normalized scores, descending
    ranked_scores = sorted(song_to_scores.items(), key=lambda x: sum(x[1]), reverse=True)

    print('############################## FINAL RANKINGS!! ##############################')
    print('Note: Normalized scores and raw values are listed in this order: [likes to reactions ratio], [likes to views ratio], [views]\n')
    for i, song_and_score in enumerate(ranked_scores):
        name, scores = song_and_score
        print(f'Rank {i + 1}: {name} with final score: {sum(scores)}')
        print(f"Normalized scores: {', '.join([str(x) for x in scores])}")
        print(f"Raw values: {', '.join([str(x) for x in song_to_stats[name]])}\n")

if __name__ == "__main__":
    print_ranking()
    