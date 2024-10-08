from dataclasses import dataclass, field
from pathlib import Path
from typing import Self, NewType

from geodepot.config import User, get_current_user
from geodepot.data import Data, DataName

CaseName = NewType("CaseName", str)


@dataclass(repr=True, order=True, unsafe_hash=True)
class CaseSpec:
    """Case specifier."""

    case_name: CaseName | None = None
    data_name: DataName | None = None

    def __str__(self):
        if self.data_name is None:
            return str(self.case_name)
        else:
            return f"{self.case_name}/{self.data_name}"

    @property
    def is_data(self):
        """Does the CaseSpec point to a data item?"""
        return self.case_name is not None and self.data_name is not None

    @property
    def is_case(self):
        """Does the CaseSpec point to a case?"""
        return self.case_name is not None and self.data_name is None

    def to_path(self) -> Path:
        if self.case_name is not None and self.data_name is not None:
            return Path(self.case_name, self.data_name)
        elif self.case_name is not None:
            return Path(self.case_name)
        else:
            Path()

    @classmethod
    def from_str(cls, casespec: str) -> Self:
        """Parse the case specifier."""
        return CaseSpec(*casespec.split("/"))


@dataclass(repr=True, order=True)
class Case:
    """A test case.

    changed_by: The User that made the last modification on the case.
    """

    name: CaseName
    description: str | None
    sha1: str | None = None
    data: dict[DataName, Data] = field(default_factory=dict)
    changed_by: User | None = None

    def add_from_path(
        self,
        source_path: Path,
        casespec: CaseSpec = None,
        data_license: str = None,
        data_format: str = None,
        data_description: str = None,
        data_changed_by: User = None,
    ) -> Data:
        data = Data(
            source_path,
            data_license=data_license,
            data_format=data_format,
            description=data_description,
            changed_by=data_changed_by,
            data_name=casespec.data_name if casespec is not None else None,
        )
        self.add_data(data)
        return data

    def add_data(self, data: Data):
        self.data[data.name] = data
        self.changed_by = data.changed_by

    def get_data(self, name: DataName) -> Data | None:
        # TODO: maybe this should take a CaseSpec as argument instead of just a DataName
        return self.data.get(name)

    def remove_data(self, name: DataName) -> Data | None:
        """Deletes the data item from the register of the Case."""
        self.changed_by = get_current_user()
        return self.data.pop(name, None)

    def to_pretty(self) -> str:
        output = [
            f"NAME={self.name}",
            f"\nDESCRIPTION={self.description}",
            f"\nnr_data_items={len(self.data)}",
            f"sha1={self.sha1}",
            f"changed_by={self.changed_by.to_pretty()}",
        ]
        return "\n".join(output)

    def compress(self):
        raise NotImplementedError

    def extract(self):
        raise NotImplementedError
