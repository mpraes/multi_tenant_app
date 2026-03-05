"""
Modelos ORM — exporta todos os models para o Alembic detectar automaticamente.

O Alembic usa Base.metadata para gerar migrações. Para que ele enxergue
um novo model, basta importá-lo aqui.

Como adicionar um novo model:
  1. Crie o arquivo em storage/models/<nome>.py com a classe SQLAlchemy
  2. Importe-o neste __init__.py
  3. Rode: alembic revision --autogenerate -m "add <nome> table"
  4. Rode: alembic upgrade head
"""

from src.storage.models.base_model import Base
from src.storage.models.configs import TenantConfigRecord
from src.storage.models.messages import MessageRecord
from src.storage.models.users import User

__all__ = ["Base", "TenantConfigRecord", "MessageRecord", "User"]
