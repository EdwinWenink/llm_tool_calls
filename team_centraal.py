import os
from typing import Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env as environment variables in runtime
load_dotenv()
USERNAME = "ChatNS"
PASSWORD = os.getenv("TEAM_CENTRAAL_PASSWORD")
BASE_URL = "https://teamcentraal.ns.nl/odata/POS_Odata_v4"
USER_AGENT = "ChatNSTEST"


class Rol(BaseModel):
    ID: int
    Rolnaam: str
    Leadrol: bool | None
    Lead: bool | None
    Ondertitel: str | None
    ClusterRol: bool | None
    ResultaatgebiedRol: bool | None


class DepartmentFinalBase(BaseModel):
    ID: int
    DepartmentId: str | None
    Parent: str | None
    Active: bool | None
    Name: str
    Description: str | None
    DepartmentFullName: str | None
    SYSID: str | None
    IsBOIT: bool | None
    Url: str | None


class ResultaatGebiedBase(BaseModel):
    ID: int
    Soort: str | None
    Naam: str | None
    Code: str | None


class TeamCentraalBetrokkene(BaseModel):
    ID: int
    Naam: str | None
    Email: str | None
    UPN: str | None
    Rol: Rol
    # Expand options
    DepartmentFinal: DepartmentFinalBase | None = None
    ResultaatGebied: ResultaatGebiedBase | None = None


class AccountBase(BaseModel):
    ID: int
    FullName: str
    Email: str


class FunctieRolsBase(BaseModel):
    ID: int
    RolNaam: str
    ScrumMasterProductOwner: str | None
    Active: bool


class TeamMemberBase(BaseModel):
    """
    Note that TeamMemberBase and TeamCentraalTeam are circularly dependent.
    By placing 'TeamCentraalTeam' in quotes, we can do a forward annotation.
    Also note that the '|' syntax does not work with forward annotation.
    """

    ID: int
    Admin: bool
    Actief: bool
    # Expand options
    Account: AccountBase | None = None
    Coach_Team: Optional["TeamCentraalTeam"] = None
    FunctieRols: list[FunctieRolsBase] | None = None
    TeamMember_Team: Optional["TeamCentraalTeam"] = None


class TeamCentraalTeam(BaseModel):
    ID: int
    Naam: str
    Ambitie: str | None
    Projecten: str | None
    Vaardigheden: str | None
    OmschrijvingTeam: str | None
    OmschrijvingTeamServiceNow: str | None
    TeamCategory: str
    WorkingOnApplications: str | None
    # Expand options
    Team_Department: DepartmentFinalBase | None = None
    TeamMembers: list[TeamMemberBase] | None = None


class TeamCentraalBetrokkeneResponse(BaseModel):
    """/Betrokkenens"""

    odata_context: str = Field(alias="@odata.context")
    value: list[TeamCentraalBetrokkene]


class TeamCentraalTeamResponse(BaseModel):
    """/Teams"""

    odata_context: str = Field(alias="@odata.context")
    value: list[TeamCentraalTeam]


class TeamCentraalTeamMemberResponse(BaseModel):
    """/Teams"""

    odata_context: str = Field(alias="@odata.context")
    value: list[TeamMemberBase]


def who_is(name: str) -> str:
    """
    Function that returns the information of a person from the Team Centraal database.
    This queries the "betrokkenens" endpoint, which is synced with Azure AD. However,
    not every "betrokkene" is part of a team and as such, I didn't find a direct link
    to relate "betrokkene" and "team". For a "betrokkene" only RG and department are linked.
    This is why we enrich the response with the `find_team_of_person` function, which
    queries starting from /TeamMembers.

    NOTE: turns out not everyone is registered as Betrokkene anyways.
    """

    endpoint = f"{BASE_URL}/Betrokkenens?$expand=ResultaatGebied,DepartmentFinal,Rol&$filter=contains(Naam, '{name}')"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }

    response = requests.get(
        endpoint, auth=(USERNAME, PASSWORD), headers=headers, timeout=60
    )
    print(response)
    print(response.status_code)
    print(response.json())

    if response.status_code == 200:
        validated_response = TeamCentraalBetrokkeneResponse.model_validate(
            response.json()
        )
        persons = validated_response.value
        answer = "\n".join(
            [
                f"{person.Naam} is {person.Rol.Rolnaam} bij {person.DepartmentFinal.Name if person.DepartmentFinal else '[onbekende afdeling]'}"
                for person in persons
            ]
        )
        return answer

    return "Persons is not found."


def find_team_member(name: str) -> str:
    """
    Queries "TeamMembers" on a person to retrieve the Team information for that person.
    Differs from "Betrokkenens" because these are not necessarily part of a team.
    It may be the case that a query returns multiple persons, for example with the same surname.
    In this case we return all information. The LLM is capable of selecting the information it needs from the original query.
    """
    endpoint = f"{BASE_URL}/TeamMembers?$expand=Account&$filter=contains(Account/FullName, '{name}')&$expand=Account,TeamMember_Team,FunctieRols"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }

    response = requests.get(
        endpoint, auth=(USERNAME, PASSWORD), headers=headers, timeout=60
    )
    print(response)
    print(response.status_code)
    print(response.json())

    if response.status_code == 200:
        validated_response = TeamCentraalTeamMemberResponse.model_validate(
            response.json()
        )
        team_members = validated_response.value

        # Everyone is part of a "Demo Team". Filter it out.
        team_members = [
            team_member
            for team_member in team_members
            if team_member.TeamMember_Team.Naam != "Demo team"
        ]

        if len(team_members) > 1:
            print("Warning: person part of multiple teams")
            for i, team in enumerate(team_members):
                print(i)
                print(team)

        def _generate_answer(team_member: TeamMemberBase):
            name = team_member.Account.FullName
            team = team_member.TeamMember_Team
            team_naam = team.Naam
            team_category = team.TeamCategory
            applicaties = team.WorkingOnApplications if team.WorkingOnApplications else ""
            projecten = team.Projecten if team.Projecten else ""
            team_omschrijving = team.OmschrijvingTeam if team.OmschrijvingTeam else ""
            team_omschrijving_snow = team.OmschrijvingTeamServiceNow  if team.OmschrijvingTeamServiceNow else ''
            vaardigheden = team.Vaardigheden if team.Vaardigheden else ''
            functie_rols = team_member.FunctieRols
            functie_beschrijving = "\n".join(
                [functie.RolNaam if functie.RolNaam != 'Overig' else 'teamlid'for functie in functie_rols]
            )
            answer = f"{name} heeft de rol {functie_beschrijving} binnen team {team_naam}, een {team_category} dat werkt aan {applicaties}{projecten}. Team beschrijving: {team_omschrijving}{team_omschrijving_snow}. Team skills: {vaardigheden}"
            return answer

        answer = "\n".join(
            [_generate_answer(team_member) for team_member in team_members]
        )
        return answer

    return "Team is not found"


def get_team_info(team_name: str) -> str:
    """
    Function that returns the information of a team from the Team Centraal database.
    """
    endpoint = f"{BASE_URL}/Teams?$filter=Naam eq '{team_name}'&$expand=TeamMembers($expand=Account,FunctieRols),Team_Department"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }

    response = requests.get(
        endpoint, auth=(USERNAME, PASSWORD), headers=headers, timeout=60
    )
    print(response)
    print(response.status_code)
    print(response.json())

    def _generate_answer(team: TeamCentraalTeam):
        department = team.Team_Department.Name if team.Team_Department else ""
        team_members = ",".join([member.Account.FullName for member in team.TeamMembers])

        team_naam = team.Naam
        team_category = team.TeamCategory
        applicaties = team.WorkingOnApplications if team.WorkingOnApplications else ""
        projecten = team.Projecten if team.Projecten else ""
        team_omschrijving = team.OmschrijvingTeam if team.OmschrijvingTeam else ""
        team_omschrijving_snow = team.OmschrijvingTeamServiceNow  if team.OmschrijvingTeamServiceNow else ''
        vaardigheden = team.Vaardigheden if team.Vaardigheden else ''

        answer = f"{team_naam} is een {team_category} team op de afdeling {department} dat werkt aan {applicaties} {projecten}."\
                    f"Beschrijving: {team_omschrijving}{team_omschrijving_snow}."\
                    f"Team skills: {vaardigheden}. De team leden zijn: {team_members}"

        return answer


    if response.status_code == 200:
        validated_response = TeamCentraalTeamResponse.model_validate(response.json())
        teams: list[TeamCentraalTeam] = validated_response.value
        answer = "\n".join([_generate_answer(team) for team in teams ])
        return answer
    else:
        return "Team is not found"


if __name__ == "__main__":
    print(find_team_member("Wenink, Edwin"))
    print(get_team_info("DIA.SIMBA"))
