from app.core.app_states import AppState
from app.services.asset import AssetService
from app.services.files import FileService
from app.services.project import ProjectService
from app.services.shot import ShotService
from app.services.task import TaskService

class LauncherData:
    """A class to handle the extraction of names from launcher data."""

    @staticmethod
    def load_data() -> list:
        """Load data into the launcher"""

        all_data = []

        # Load projects
        project_list = ProjectService.get_user_project()
        for project in project_list:
            project_id = project.get("id")

            task_list = TaskService.get_task_types_by_project(project_id)
            asset_list = AssetService.get_asset_types_by_project(project_id)

            project_data = {
                "project_id": project_id,
                "project": project.get("name"),
                "episodes": [],
                "tasks": [
                    {"task_id": task["id"], "task": task["name"], "task_for_entity": task["for_entity"]}
                    for task in task_list
                ],
                "assets": [
                    {"asset_id": asset["id"], "asset": asset["name"]} for asset in asset_list
                ]
            }
            # Load episodes for each project
            episode_list = ShotService.get_episode_by_project(project_id)
            for episode in episode_list:
                episode_id = episode.get("id")
                episode_data = {
                    "episode_id": episode_id,
                    "episode": episode.get("name"),
                    "sequences": []
                }
                # Load sequences for each episode
                sequence_list = ShotService.get_sequence_by_episode(episode_id)
                for sequence in sequence_list:
                    sequence_id = sequence.get("id")
                    sequence_data = {
                        "sequence_id": sequence_id,
                        "sequence": sequence.get("name"),
                        "shots": []
                    }
                    # Load shots for each sequence
                    shots = ShotService.get_shots_by_sequence(sequence_id)
                    shot_data = []
                    for shot in shots:
                        shot_data.append({
                            "shot_id": shot.get("id"),
                            "shot": shot.get("name"),
                        })

                    sequence_data["shots"] = shot_data
                    episode_data["sequences"].append(sequence_data)
                project_data["episodes"].append(episode_data)
            all_data.append(project_data)
        # print(f"All Data: {all_data}")
        return all_data


    @staticmethod
    def extract_all_name_id(data: list) -> list:
        results = []

        for project in data:
            if "project" in project and "project_id" in project:
                results.append({
                    "name": project["project"],
                    "id": project["project_id"]
                })

            # Assets
            for asset in project.get("assets", []):
                if "name" in asset and "id" in asset:
                    results.append({
                        "name": asset["name"],
                        "id": asset["id"]
                    })

            # Tasks
            for task in project.get("tasks", []):
                if "name" in task and "id" in task:
                    results.append({
                        "name": task["name"],
                        "id": task["id"]
                    })

            # Episodes
            for episode in project.get("episodes", []):
                if "episode" in episode and "episode_id" in episode:
                    results.append({
                        "name": episode["episode"],
                        "id": episode["episode_id"]
                    })

                # Sequences
                for sequence in episode.get("sequences", []):
                    if "sequence" in sequence and "sequence_id" in sequence:
                        results.append({
                            "name": sequence["sequence"],
                            "id": sequence["sequence_id"]
                        })

                    # Shots
                    for shot in sequence.get("shots", []):
                        if "shot" in shot and "shot_id" in shot:
                            results.append({
                                "name": shot["shot"],
                                "id": shot["shot_id"]
                            })

        return results