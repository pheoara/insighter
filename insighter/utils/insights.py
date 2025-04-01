import json
from insighter.pipelines.insights import insight_pipeline

def run_insight_pipeline(file_path):

    insights = insight_pipeline(file_path=file_path)  
    json_path = file_path.replace('.csv', '.json')

    with open(json_path, 'w') as f:
        json.dump(insights, f)
        
    return insights