import React, {useEffect, useState} from "react";
import {Button, Dropdown, Table} from "react-bootstrap";
import {getCookie, SUB_STATE_OPTIONS} from "../scripts/utils";
import Select from "react-dropdown-select";
import {EditableField} from "./Shared";
import {toast} from "react-toastify";

export const SEX_DISPLAY_MAP = {
  "male": "M",
  "female": "K",
  "other": "I",
};

const getSexDisplay = (s) => {
  return SEX_DISPLAY_MAP[s] || s;
};

export const CURRENT_PLACE_DISPLAY_MAP = {
  "inPoland": "w Polsce",
  "onBorder": "na granicy",
};

const getCurrentPlaceDisplay = (place) => {
  return CURRENT_PLACE_DISPLAY_MAP[place] || place;
};

const getStatusDisplay = (status) => {
  const option = SUB_STATE_OPTIONS.filter(o => o.value === status)[0];
  return option.label;
};

const statusAsNumber = (value) => {
  switch (value) {
    case "new":
      return 0;
    case "searching":
      return 1;
    case "in_progress":
      return 2;
    case "cancelled":
      return 3;
    case "success":
      return 4;
    default:
      return 10;
  }
};


const updateSub = (sub, fields, onCorrect = null) => {

  fetch(`/api/sub/update/${sub.id}`, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    headers: {
      'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')
    }, body: JSON.stringify({fields: fields}) // body data type must match "Content-Type" header
  }).then(response => response.json()).then(data => {

    if (data.status === "success") {
      if (onCorrect) {
        onCorrect();
      }
    } else {
      throw new Error(data.message);
    }
    // toast(`${data.message}`, {type: data.status});
  }).catch((error) => {
    console.error('Error:', error);
    toast(`THERE WAS AN ERROR:\n${error}`, {type: "error", autoClose: 3000});
  });
};


export function SubmissionRow({sub, activeHandler, user, isGroupCoordinator, isActive = false, readOnly = false}) {


  const isGroupAdmin = isGroupCoordinator;
  const isOwner = user.id === sub.matcher?.id;
  const isCoordinator = user.id === sub.coordinator?.id;
  const [status, setStatus] = useState(sub.status);
  const [note, setNote] = useState(sub.note);
  const [when, setWhen] = useState(sub.when);
  const [localSub, setLocalSub] = useState(sub);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    setLocalSub(sub);
    setNote(sub.note);
    setWhen(sub.when);
    setStatus(sub.status);
  }, [sub]);

  const btnHandler = () => {
    if (readOnly) {
      return;
    }

    activeHandler(sub, isActive);
  };



  const getActionBtn = () => {
    if (readOnly || isActive || statusAsNumber(localSub.status) > 2) {
      return "";
    }
    if (localSub.status === "in_progress") {
      if (localSub.coordinator) {
        return "";
      } else {
        return <Button size={"sm"} onClick={setCoordinator}>Przypisz do siebie</Button>;
      }
    } else if (localSub.status === "searching" && !isOwner) {
      return "";
    } else if (localSub.matcher && !isActive && !isOwner) {
      return <Button size={"sm"} disabled>{localSub.matcher.display}</Button>;
    } else if (localSub.status === "cancelled") {
      return "NIEAKTUALNE";
    } else {
      return <Button className={"w-100"} size={"sm"} onClick={btnHandler}>{isActive ? "Zwolnij" : "Szukaj Hosta"}</Button>;
    }
  };

  const updateStatus = (value) => {

    const newStatus = value[0].value;
    if (newStatus !== localSub.status) {

    if (isActive === true) {
      updateSub(localSub, {"status": newStatus, matcher: null}, () => {
        setStatus(newStatus);
        setLocalSub((s) => ({...s, status: newStatus, matcher: null}));
        activeHandler(sub, true, false);
      });
    } else {
      updateSub(localSub, {"status": newStatus}, () => {
        setStatus(newStatus);
        setLocalSub((s) => ({...s, status: newStatus}));
      });
    }


    } else {

    }
  };

  const freeUpMatcher = () => {
    updateSub(sub, {"matcher": null, "status": "new"}, () => {
      setStatus("new");
      setLocalSub((s) => ({...s, matcher: null}));
    });
  };

  const freeUpCoord = () => {
    updateSub(sub, {"coordinator": null}, () => {
      setLocalSub((s) => ({...s, coordinator: null}));
    });
  };


  const setCoordinator = () => {

    fetch(`/api/sub/update/${localSub.id}`, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      headers: {
        'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')
      }, body: JSON.stringify({fields: {"coordinator_id": user.id}}) // body data type must match "Content-Type" header
    }).then(response => response.json()).then(data => {

      // toast(`${data.message}`, {type: data.status});
      setLocalSub(s => ({...s, coordinator: user}));
    }).catch((error) => {
      console.error('Error:', error);
    });
  };

  const getStatusClass = (sub) => {
   if (sub.status === "in_progress" && sub.resource?.will_pick_up_now) {
     return "sub-in-progress-host-coming";
   }
   if (sub.is_suspend === true) {
     return "sub-suspend";
   }
    return `sub-${localSub.status.replace("_", "-")}`;
  };

  return <div
      className={`submission-row ${getStatusClass(localSub)}
      ${localSub.accomodation_in_the_future ? "sub-in-future" : ""} ${isActive ? "sub-active" : ""}`}>
    <div className="sub-id position-relative">
      ID ZGŁOSZENIA: {localSub.id}

      <div className="submission-row-collapse cursor-pointer" onClick={() => setCollapsed(!collapsed)}>
        Zwiń / Rozwiń
      </div>
    </div>
    <Table className="sub-table" style={{'background-color': 'rgba(255, 255, 255, 0.95)', display: collapsed ? 'none' : 'table'}}>
      <tbody>
      <tr>
        <th>Imię i nazwisko</th>
        <td>{localSub.name}</td>
        <th>Osoby</th>
        <td>
          {
            [
              localSub.adults ? ('Dorośli - ' + localSub.adults.length + ': ' + (localSub.adults.map(adult => getSexDisplay(adult.sex) + '/' + adult.ageRange)).join(', ')) : '',
              localSub.children ? ('Dzieci - ' + localSub.children.length + ': ' + (localSub.children.map(child => getSexDisplay(child.sex) + '/' + child.ageRange)).join(', ')) : '',
              localSub.people
            ].filter(e => e).map(e => <div key={e}>{e}</div>)
          }
        </td>
        <th>Jak dlugo?</th>
        {/*todo: translation*/}
        <td>
          {[localSub.how_long, localSub.how_long_other].filter(l => l).join(', ')}
        </td>
        <th>Kontakt</th>
        <td>{localSub.phone_number + ', ' + localSub.email}</td>
      </tr>
      <tr>
        <th>Od Kiedy?</th>
        <td>
          <input required type="date" min={new Date().toJSON().slice(0, 10)} value={when} onChange={(e) => {
            let newWhenDate = e.target.value;
            updateSub(localSub, {"when": newWhenDate}, () => setWhen(newWhenDate));
          }}/>
        </td>
        <th>Opis:</th>
        <td>{localSub.description}</td>
        <th>Języki</th>
        <td>{localSub.languages.map(lang => lang.namePl).concat(localSub.languages_other).filter(l => l).join(", ")}</td>
        <th>Rozważane województwa</th>
        <td>{localSub.voivodeships ? localSub.voivodeships.map(voivodeship => voivodeship.namePl).map(e => <div key={e}>{e}</div>) : <div>Wszystkie</div>}</td>
      </tr>
      <tr>
        <th>Dodatkowe potrzeby</th>
        <td>{localSub.additional_needs.map(n => n.namePl).concat(localSub.additional_needs_other).filter(e => e).map(e => <div key={e}>{e}</div>)}</td>
        <th>Alergie</th>
        <td>{localSub.allergies.map(n => n.namePl).concat(localSub.allergies_other).filter(e => e).map(e => <div key={e}>{e}</div>)}</td>
        <th>Osoby narażone</th>
        <td>{localSub.groups.map(n => n.namePl).concat(localSub.groups_other).filter(e => e).map(e => <div key={e}>{e}</div>)}</td>
        <th>Plany</th>
        <td>{localSub.plans.map(n => n.namePl).concat(localSub.plans_other).filter(e => e).map(e => <div key={e}>{e}</div>)}</td>
      </tr>
      <tr>
        <th>Obecna lokalizacja</th>
        <td>{getCurrentPlaceDisplay(localSub.currentPlace)}</td>
        <th>Pierwsze zgłoszenie?</th>
        <td>{localSub.first_submission ? 'Tak' : 'Nie'}</td>
        <th>Notka</th>
        <td>
          <EditableField value={note} onRename={(note) => updateSub(localSub, {"note": note}, () => setNote(note))}/>
        </td>
      </tr>
      {localSub.resource && <tr className="tr-host">
        <th>HOST</th>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td colSpan={3}></td>
      </tr>}
      {localSub.resource && <tr className="tr-host">
        <th>Kontakt host:</th>
        <td >{localSub.resource.name} ({localSub.resource.phone_number})</td>
        <th>Adres hosta:</th>
        <td>{localSub.resource.address}</td>
        <th>Notatka:</th>
        <td colSpan={3}>{localSub.resource.note}</td>
      </tr>}
      <tr className={localSub.resource?"tr-host":""}>
        <th>{["searching", "new"].includes(localSub.status) ? "Hosta szuka" : "Host znaleziony przez"}</th>
        <td>{localSub.matcher?.display || ""}</td>
        <th>Akcja</th>
        <td>{getActionBtn()}</td>
        <th>
          Status
        </th>
        <td>
          {isGroupAdmin ? <Select
              values={SUB_STATE_OPTIONS.filter((o) => o.value === status)}
              options={SUB_STATE_OPTIONS}
              onChange={updateStatus}
          /> : (isActive? <Select
              values={SUB_STATE_OPTIONS.filter((o) => o.value === status)}
              options={SUB_STATE_OPTIONS.filter((o) =>
                  (o.value === status || o.value === 'contact_attempt'))
              }
              onChange={updateStatus}
          />: getStatusDisplay(status))
          }
        </td>
      </tr>
      {isCoordinator && !isGroupAdmin && statusAsNumber(localSub.status) < 3 && <tr>
        <td className={"text-center"} colSpan={2}><Button variant={"secondary"} size={"sm"} onClick={() => updateStatus([{value: "cancelled"}])}>Nieaktualne</Button></td>
        <td colSpan={4}/>
        <td className={"text-center"} colSpan={2}><Button variant={"success"} size={"sm"} onClick={() => updateStatus([{value: "success"}])}>Sukces</Button></td>
      </tr>}
      {isActive && !readOnly && statusAsNumber(localSub.status) < 3 && <tr>
        <td className={"text-center"} colSpan={2}><Button variant={"secondary"} size={"sm"}
                                                          onClick={() => activeHandler(sub, true, true)}>Nieaktualne</Button>
        </td>
        <td colSpan={4}/>
        <td className={"text-center"} colSpan={2}><Button variant={"primary"} size={"sm"}
                                                          onClick={btnHandler}>Zwolnij</Button>
        </td>
      </tr>}
      {isGroupAdmin && !isActive && !readOnly && <tr className="no-striping">
        <th>Akcje koordynatora</th>
        <td colSpan={2} className={"text-center"}>
          {localSub.matcher &&
              <Button variant={"danger"} size={"sm"} onClick={freeUpMatcher}>Zwolnij zgłoszenie</Button>}
        </td>
        <td colSpan={2} className={"text-center"}>
          {localSub.coordinator &&
              <Button variant={"secondary"} size={"sm"} onClick={freeUpCoord}>Zwolnij łącznika</Button>}
        </td>
      </tr>}
      </tbody>
    </Table>
    <p className="sub-id">Przyjęte: {localSub.created}</p>
  </div>;
}
