from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.database.session import get_all_objects_by_filter

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_list(self) -> List[User]:
        """Get all users"""
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_x_user_id(self, x_user_id: int) -> Optional[User]:
        """Get user by Twitter user ID"""
        result = await self.db.execute(select(User).filter(User.x_user_id == x_user_id))
        return result.scalar_one_or_none()

    async def get_empty_ai_role_id_user_list(self) -> List[User]:
        """Get all users with empty AI role ID"""
        return await get_all_objects_by_filter(self.db, User, ai_role_id=None)

    async def get_user_by_wallet_address(self, wallet_address: str) -> Optional[User]:
        """Get user by wallet address"""
        result = await self.db.execute(select(User).filter(User.wallet_address == wallet_address))
        return result.scalar_one_or_none()

    async def update_user_role_by_user_id(self, user_id: int, role_id: str) -> None:
        """Update user's AI role ID"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(ai_role_id=role_id)
        )
        await self.db.commit()

    async def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user data"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**user_data)
        )
        await self.db.commit()
        return await self.get_user_by_id(user_id)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
