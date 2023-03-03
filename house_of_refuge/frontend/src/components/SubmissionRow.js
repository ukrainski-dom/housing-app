import React, {useEffect, useState} from "react";
import {Button, Dropdown, Table} from "react-bootstrap";
import {getCookie, SUB_STATE_OPTIONS} from "../scripts/utils";
import Select from "react-dropdown-select";
import {EditableField} from "./Shared";
import {toast} from "react-toastify";

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
  const [localSub, setLocalSub] = useState(sub);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    setLocalSub(sub);
    setNote(sub.note);
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
        <th>Ile Osób?</th>
        <td>Dorośli - 3: Ż/43, M/50, I/22<br/>Dzieci - 3: Ż/12, M/6, I/15</td>
        <th>Jak dlugo?</th>
        <td>
          На два місяці і більше
        </td>
        <th>Kontakt</th>
        <td>{localSub.phone_number + ', ' + localSub.email}</td>
      </tr>
      <tr>
        <th>Od Kiedy?</th>
        <td>
          26/12/2022
        </td>
        <th>Opis:</th>
        <td>{localSub.description}</td>
        <th>Języki</th>
        <td>{localSub.languages.map(function (lang) {
          return lang.namePl;
        }).join(", ")}</td>
        <th>Lokalizacja</th>
        <td>Mazowieckie - Warszawa (03-984)</td>
      </tr>
      <tr>
        <th>Dodatkowe potrzeby</th>
        <td>Dodatkowe potrzeby,,,</td>
        <th>Alergie</th>
        <td>Alegrie....</td>
        <th>Osoby narażone</th>
        <td>ЛГБТКA+; Особа з неповносправністю (самостійна)</td>
        <th>Plany</th>
        <td>Plany...</td>
      </tr>
      <tr>
        <th>Pierwsze zgłoszenie?</th>
        <td>Tak</td>
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
        <td>{localSub.matcher?.display || getActionBtn()}</td>
        <th>Łącznik</th>
        <td>{localSub.coordinator?.display || (localSub.matcher ? getActionBtn() : "")}</td>
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
        <td colSpan={1} className={"text-center"}>
          <Dropdown>
            <Dropdown.Toggle variant="secondary" size={"sm"}>
              Zmień źródło
            </Dropdown.Toggle>

            <Dropdown.Menu>
              <Dropdown.Item disabled={localSub.source === "terrain"}
                             onClick={() => updateSub(localSub, {source: "terrain"})}>Zachodni</Dropdown.Item>
              <Dropdown.Item disabled={localSub.source === "webform"}
                             onClick={() => updateSub(localSub, {source: "webform"})}>Strona</Dropdown.Item>
              <Dropdown.Item disabled={localSub.source === "mail"}
                             onClick={() => updateSub(localSub, {source: "mail"})}>Email</Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </td>
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
