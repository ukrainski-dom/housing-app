import React, {useEffect, useState} from "react";
import {Button, ButtonGroup, Modal, Table} from "react-bootstrap";
import {getCookie, getPickUpDisplay, updateResource} from "../scripts/utils";
import {EditableField} from "./Shared";
import {SubmissionRow} from "./SubmissionRow";

export const shortCols = ["people_to_accommodate"];

const MatchModal = ({showModal, handleClose, matchHandle, resource, activeSub, user}) => {

  const [dateSet, setDateSet] = useState(null);
  const [success, setSuccess] = useState(false);

  const match = (transport) => {
    const payload = {transport: transport, newDate: dateSet};
    matchHandle(resource, payload);
    handleClose();
  };

  const toIgnore = () => {
    updateResource(resource, {status: "ignore", owner: null}, () => handleClose());
  };

  const noAnswer = () => {
    updateResource(resource, {status: "contact_attempt", owner: null}, () => handleClose());
  };

  const bookHost = () => {
    updateResource(resource, {status: "booked", owner: user.id});
  };

  const close = () => {
    if (resource.status !== "booked") {
      updateResource(resource, {status: "new", owner: null}, () => handleClose());
      return;
    }
    handleClose();
  };

  const notToday = () => {
    // TODO: update note with last contact info?
    const payload = {status: "new", availability: dateSet, owner: null};
    updateResource(resource, payload, () => handleClose());
  };

  const handleDateChange = (e) => {
    const newDate = e.target.value;
    setDateSet(newDate);
  };


  return (<Modal show={showModal} onHide={noAnswer} className="" dialogClassName="" backdrop="static"
                 keyboard={false}  fullscreen={true}
  >
    <Modal.Body className={"text-center"}>
      <SubmissionRow sub={activeSub} isActive={true} readOnly={true} user={resource.owner || {}}/>
      <ResourceRow resource={resource} isExpanded={true} isCoordinator={false} compact={true}/>
      <h6>Od kiedy host będzie znów dostępny?</h6>
      <h6>( Kiedy raz jeszcze możemy do Pani/Pana przedzwonić? )</h6>
      <div style={{margin: "30px"}}>
        <input required type="date" min={new Date().toJSON().slice(0, 10)} value={dateSet}
               onChange={handleDateChange}/>
      </div>
      {   <div className={"host-call-buttons"}>
            <Button variant="success" disabled={!dateSet} onClick={() => match(true)}>
              Zgodził się wziąć!
            </Button>
            <Button disabled={resource.status==="booked"} onClick={bookHost}>
              Rezerwacja czasowa
            </Button>
            <Button variant="warning" disabled={!dateSet} onClick={notToday}>
              Nie weźmie
            </Button>
          </div>
      }
    </Modal.Body>
    <Modal.Footer className={"justify-content-around"} >
      <Button variant="danger" onClick={() => setSuccess(toIgnore)}>
        Do wywalenia
      </Button>
      <Button className={"mx-auto"} variant="secondary" onClick={noAnswer}>
        Nie odbiera
      </Button>
      <Button variant="secondary" onClick={close}>
        Wróć
      </Button>
    </Modal.Footer>
  </Modal>);
};

const VISIBLE = ["name", "full_address", "people_to_accommodate", "accommodation_length", "resource"];

const STATUS_OPTIONS = [
  {label: "Nowy", value: "new"},
  // {label: "Zajęta", value: "taken"},
  {label: "Zignoruj", value: "ignore"},
];

export const RESOURCE_MAP = {
  "home": "Dom",
  "flat": "Mieszkanie",
  "room": "Pokój",
  "couch": "Kanapa",
  "mattress": "Materac",
  "two_rooms": "Dwa pokoje",
  "room_in_own_house": "Pokój w domu lub w mieszkaniu, gdzie mieszkasz",
  "separate_part_of_apartment": "Wydzielona część domu czy lokalu, w którym przebywają inni ludzie",
  "bed_in_shared_room": "Łóżko w pokoju współdzielonym",
  "place_in_hotel": "Miejsce w hotelu, hostelu, pensjonacie"
};

const getResourceDisplay = (r) => {
  return RESOURCE_MAP[r] || r;
};

const getReadyDisplay = (resource) => {
  if (resource.is_dropped) {
    return "Zniknięty";
  }
  if (resource.is_ready) {
    return "Gotowy do wzięcia kogoś teraz!";
  }
  if (resource.cherry) {
    return "Wisienka 🍒";
  }
  if (resource.verified) {
    return "Zweryfikowany";
  }
};

export const ResourceRow = ({resource, isExpanded, onMatch, user, activeSub, compact = false, isCoordinator = false}) => {
  const [expanded, setExpanded] = useState(isExpanded);
  const [showModal, setShowModal] = useState(false);
  const [availableFrom, setAvailableFrom] = useState(resource.availability);
  const [note, setNote] = useState(resource.note);
  const [hide, setHide] = useState(false);

  useEffect(() => {
    setNote(resource.note);
    setAvailableFrom(resource.availability);
  }, [resource]);


  useEffect(() => {
    return () => {
      setExpanded(isExpanded);
    };
  }, [isExpanded]);

  const updateNote = (value) => {

    fetch(`/api/update_note/${resource.id}`, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      headers: {
        'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')
      }, body: JSON.stringify({"note": value}) // body data type must match "Content-Type" header
    }).then(response => response.json()).then(data => {

      // toast(`${data.message}`, {type: data.status});
      setNote(value);
    }).catch((error) => {
      console.error('Error:', error);
    });
  };

  const handleDateChange = (e) => {
    const newDate = e.target.value;
    updateResource(resource, {"availability": newDate});
    setAvailableFrom(newDate);
  };

  const isTaken = () => {
    return (resource.status  === "calling" || resource.status === "booked");
  };

  const showStatus = () => {
    switch (resource.status) {
      case "calling":
        return "dzwoni ".concat(resource.owner.display);
      case "booked":
        return "rezerwacja ".concat(resource.owner.display);
      case "new":
        return "nowy";
      default:
        return resource.status;
    }
  };

  const openHost = () => {
    if (isTaken()) {
      setShowModal(true);
      return;
    }
    updateResource(resource, {status: "calling", owner: user.id}, () => setShowModal(true));
  };

  if (hide) {
    return <></>;
  }

  return <div className={`resource-row`}>
    <div className={`base-content row-${resource.status}
      ${resource.verified ? "row-verified" : ""} ${resource.cherry ? "row-cherry" : ""}
      ${resource.is_ready ? "row-ready" : ""}
      ${resource.is_dropped ? "row-dropped" : ""}
      `}>
      <div className={"col r-id-col"}>{resource.id}</div>
      {VISIBLE.map((a) => <div onClick={() => setExpanded(e => !e)}
                               className={`col ${shortCols.includes(a) ? "col-short" : ""}`}
                               key={`${resource.id}-${a}`}>{getResourceDisplay(resource[a])}</div>)}
      <div className={"col col-availability"}>
        {compact ? getPickUpDisplay(resource.will_pick_up_now) :
            <input required type="date" min={new Date().toJSON().slice(0, 10)} value={availableFrom}
                   onChange={handleDateChange}/>}
      </div>
      <div className={`col no-pointer col-hot-sort`}>
        {compact ? resource.note :
            <ButtonGroup aria-label="Basic example">
              <Button variant={resource.is_hot ? "success" : "outline-success"} size={"sm"}
                      onClick={() => updateResource(resource, {got_hot: resource.is_hot ? null : new Date().toISOString()})}>
                🔥
              </Button>
              <Button variant={resource.cherry ? "success" : "outline-success"}
                      onClick={() => updateResource(resource, {"cherry": !resource.cherry})}>
                🍒
              </Button>
              <Button variant={resource.verified ? "success" : "outline-success"}
                      onClick={() => updateResource(resource, {"verified": !resource.verified})}
              >👍
              </Button>
              <Button variant={resource.turtle ? "success" : "outline-success"}
                      onClick={() => updateResource(resource, {"turtle": !resource.turtle})}
              >🐢
              </Button>
            </ButtonGroup>
        }
      </div>
      {compact && isCoordinator && <div className={`col col-short`}>
        <Button variant={"info"} size={"sm"}
                onClick={() => updateResource(resource, {is_dropped: false}, () => setHide(true))}
        >zwolnij</Button>
      </div>}
    </div>
    {expanded && <div className="row-expanded">
      <Table bordered style={{borderColor: 'black'}}>
        <tbody>
        <tr>
          <th>Języki</th>
          {/* FIXME: workaround to use unused languages field as call hint */}
          <td>{resource.languages.map(lang => lang.namePl).concat(resource.languages_other).filter(l => l).join(", ")}</td>
          <th>Od kiedy?</th>
          <td>{resource.availability}</td>
          <th>Na ile?</th>
          <td>{resource.how_long}</td>
        </tr>
        <tr>
          <th>Dodatkowe informacje</th>
          <td>{[resource.details, resource.about_info].filter(l => l).join("||")}</td>
          <th>Zwierzęta w domu</th>
          <td>{resource.animals.map(n => n.namePl).concat(resource.animals_other).filter(e => e).map(e => <div key={e}>{e}</div>)}</td>
          <th>Udogodnienia</th>
          <td>
            <ul>
              {resource.facilities.map(n => n.namePl).concat(resource.facilities_other).filter(e => e).map(e => <li key={e}>{e}</li>)}
            </ul>
          </td>
        </tr>
        <tr>
          <th>Ile osób?</th>
          <td>{resource.extra ? resource.extra : 'Dorośli: ' + resource.adults_max_count + ' Dzieci: ' + resource.children_max_count}</td>
          <th>Mogę zakwaterować</th>
          <td>{resource.groups.map(n => n.namePl).concat(resource.groups_other).filter(e => e).map(e => <div key={e}>{e}</div>)}</td>
          <th>Kontakt</th>
          <td>{resource.phone_number + ' ' + resource.email}</td>
        </tr>
        <tr>
          <th>Notatka</th>
          <td><EditableField value={note} onRename={updateNote}/></td>

          <th>Status</th>
          <td>{showStatus()}</td>

          {compact ?
              <s/>
              :
              <>
                <td className={"text-center"}>{getReadyDisplay(resource)}</td>
                <td className={"text-center"}>
                  <Button size={"sm"}
                          disabled={isTaken() && resource.owner.id !== user.id}
                          onClick={openHost}>
                    {isTaken() ? `DZWONI ${resource.owner?.display}` : "DZWONIĘ"}
                  </Button>
                </td>
              </>
          }
        </tr>
        </tbody>
      </Table>

    </div>}
    {!compact &&
        <MatchModal showModal={showModal} handleClose={() => setShowModal(false)} resource={resource}
                    matchHandle={onMatch} activeSub={activeSub} user={user}/>
    }
  </div>;
};
