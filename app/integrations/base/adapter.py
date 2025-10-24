from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    @abstractmethod
    def get_project(self, project_id: str):
        """Fetch metadata for a single project/list/board/etc."""
        pass

    @abstractmethod
    def get_tasks(self, project_id: str):
        """Fetch tasks belonging to a project/list/board/etc."""
        pass

    @abstractmethod
    def transform_project(self, raw_data: dict) -> dict:
        """Convert provider-specific project into universal format."""
        pass

    @abstractmethod
    def transform_task(self, raw_data: dict) -> dict:
        """Convert provider-specific task into universal format."""
        pass
