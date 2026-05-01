from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.persistence.models import ServiceEntity, InteractionLogEntity
from app.core.domain.models import VirtualServiceConfig

class ServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_service(self, config: VirtualServiceConfig):
        # Update or create
        stmt = select(ServiceEntity).where(ServiceEntity.name == config.service_name)
        result = await self.session.execute(stmt)
        entity = result.scalars().first()

        if not entity:
            entity = ServiceEntity(name=config.service_name)
            self.session.add(entity)
        
        entity.type = config.service_type
        entity.input_queue = config.input_queue
        entity.output_queue = config.output_queue
        entity.is_active = config.active
        entity.is_stateful = config.stateful
        entity.config_json = config.model_dump()
        
        await self.session.commit()

    async def get_all_services(self) -> List[VirtualServiceConfig]:
        stmt = select(ServiceEntity)
        result = await self.session.execute(stmt)
        entities = result.scalars().all()
        return [VirtualServiceConfig(**e.config_json) for e in entities]

    async def get_service_by_name(self, name: str) -> Optional[VirtualServiceConfig]:
        stmt = select(ServiceEntity).where(ServiceEntity.name == name)
        result = await self.session.execute(stmt)
        entity = result.scalars().first()
        if entity:
            return VirtualServiceConfig(**entity.config_json)
        return None

    async def delete_service(self, name: str):
        stmt = select(ServiceEntity).where(ServiceEntity.name == name)
        result = await self.session.execute(stmt)
        entity = result.scalars().first()
        if entity:
            await self.session.delete(entity)
            await self.session.commit()
