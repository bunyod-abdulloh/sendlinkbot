from aiogram import BaseMiddleware, types
from collections import defaultdict


class CountInvitesMiddleware(BaseMiddleware):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.invites_to_update = defaultdict(int)  # inviter -> new_member_count

    async def __call__(self, handler, event: types.Update, data: dict):
        # Faqat ChatMemberUpdated turlariga ishlaydi
        if isinstance(event, types.ChatMemberUpdated):
            # A'zo qo'shish hodisasini tekshirish
            if event.new_chat_member.status == "member":
                inviter_id = event.from_user.id
                new_member_id = event.new_chat_member.user.id

                # Foydalanuvchi qo'shilganda invite_countni yangilash
                self.invites_to_update[inviter_id] += 1
                print(
                    f"Inviter {inviter_id} added {new_member_id}. Total invites: {self.invites_to_update[inviter_id]}")

        # Batch update - Har bir so'rovni yuborganimizda hammasini yangilash
        if len(self.invites_to_update) > 0:
            await self.batch_update_invites()
            self.invites_to_update.clear()

        # Keyingi handlerni chaqirish
        return await handler(event, data)

    async def batch_update_invites(self):
        # Batch update qilish uchun DBga so'rov yuborish
        queries = []
        for inviter, count in self.invites_to_update.items():
            queries.append(
                f"""
                INSERT INTO Users (inviter, new_member, invite_count)
                VALUES ($1, $2, {count})
                ON CONFLICT (new_member) DO UPDATE
                SET invite_count = Users.invite_count + {count}
                """
            )
        # DBga barcha so'rovlarni yuborish
        for query in queries:
            await self.db.execute(query, fetch=True)
