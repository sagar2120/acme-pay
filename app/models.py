from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

LEVELS = ["L1", "L2", "L3", "L4", "L5", "L6"]


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(80))
    country: Mapped[str] = mapped_column(String(80))
    currency: Mapped[str] = mapped_column(String(3))


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[str] = mapped_column(String(15), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), index=True)
    email: Mapped[str] = mapped_column(String(160), unique=True)
    job_title: Mapped[str] = mapped_column(String(80))
    level: Mapped[str] = mapped_column(String(2), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), index=True)
    hire_date: Mapped[date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(default=True)

    location: Mapped[Location] = relationship()
    department: Mapped[Department] = relationship()


class PayRecord(Base):
    __tablename__ = "pay_record"
    __table_args__ = (
        UniqueConstraint("employee_id", "effective_from", name="one_pay_change_per_day"),
        Index("pay_record_newest_first", "employee_id", "effective_from"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employee.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    amount_usd: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    effective_from: Mapped[date] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(String(500))


class FxRate(Base):
    __tablename__ = "fx_rate"

    currency: Mapped[str] = mapped_column(String(3), primary_key=True)
    usd_per_unit: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    as_of: Mapped[date] = mapped_column(Date)
