from base.abstracts.service_base import ServiceBase
from base.models import ToDo


class GetToDoService(ServiceBase):
    def __init__(self, todos=None, *args, **kwargs):
        self._todos = todos
        super().__init__(*args, **kwargs)

    def _perform(self):
        todos_query = ToDo.objects.all()

        data = []
        for todo in todos_query:
            data.append(
                {
                    "title": todo.Title,
                    "description": todo.Description,
                    "date": todo.Date,
                    "completed": todo.Completed
                }
            )

        return (True, "As tuas tarefas foram retornadas com sucesso!", data)
