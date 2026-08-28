from sqlalchemy import Numeric, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from decimal import Decimal
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    coin: Mapped[str | None] 
    action: Mapped[str | None]
    amount: Mapped[Decimal | None] = mapped_column(Numeric())
    price: Mapped[Decimal | None] = mapped_column(Numeric())
    total: Mapped[Decimal | None] = mapped_column(Numeric())
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Transaction(id={self.id}, coin='{self.coin}', action='{self.action}', amount={self.amount}, price={self.price}, total={self.total})>"