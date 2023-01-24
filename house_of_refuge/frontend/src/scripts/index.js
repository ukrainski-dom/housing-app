import "../styles/resources.scss";
import React, {useEffect, useState} from 'react'; // eslint-disable-line
import ReactDOM from 'react-dom';
import {
  getCookie,
  getHelped,
  getLatestHostTimestamp,
  getLatestSubId,
  getRandomInt,
  shouldShowHost,
  strToBoolean,
  SUB_STATE_OPTIONS
} from "./utils";
import {toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {ResourceList} from "../components/ResourceList";
import {SOURCE_OPTIONS, SubmissionList} from "../components/SubmissionList";
import useInterval from "use-interval";
import {BrowserRouter, Route, Routes, useSearchParams} from "react-router-dom";

var UPDATE_LOOP_IS_PROCESSING = false;


const CoordinatorsHeader = ({coordinators, helped, hide}) => {
  const [peopleHelped, setPeopleHelped] = useState(helped);
  const [collapsed, setCollapsed] = useState(false);
  const all_coordinators = (coordinators.station || []).concat(coordinators.remote || [])

  useInterval(async () => {
    const newHelped = await getHelped();
    setPeopleHelped(newHelped);
  }, 120 * 1000);

  return <div className="panel-header mx-5 mt-1" style={hide ? {display: "none"} : {}}>
    <div>
      <img src="/static/images/logo.svg" alt="logo" style={{height: "76px", margin: "10px 0", display: collapsed ? 'none' : 'block'}}/>
    </div>
    <div className="coordinators" style={{ display: collapsed ? 'none' : 'block' }}>
      <div className="d-flex justify-content-around">
        <div className={"mx-5 text-center"}>
          <h5>Koordynatorzy</h5>
            <ol>{all_coordinators.map(c => <li key={c.user.id}>{c.user.display}</li>)}</ol>
        </div>
      </div>
      {peopleHelped ?
          <div><h5 className="good-message">Pomogliśmy
            dziś {peopleHelped} osobom {"🙏".repeat(Math.floor(peopleHelped / 10))}</h5>
          </div> : <></>}
    </div>
    <div>
      <span className={"mx-2 btn btn-primary btn-sm"} onClick={() => setCollapsed(!collapsed)}>
        { collapsed ? 'pokaż ' : 'ukryj ' }
        nagłówek
      </span>
      <a className={"btn btn-danger btn-sm"} href="/accounts/logout">wyloguj się</a>
    </div>
  </div>;
};


const App = ({subs, userData, coordinators, helped}) => {
  let [searchParams, setSearchParams] = useSearchParams();


  const [tabVisible, setTabVisible] = useState(true);
  const [activeSub, setActiveSub] = useState(null);
  const [sourceFilter, setSourceFilter] = useState(searchParams.getAll("z").map((i) => SOURCE_OPTIONS[i]));
  const [statusFilter, setStatusFilter] = useState(searchParams.getAll("s").map(i => SUB_STATE_OPTIONS[i]));
  const [peopleFilter, setPeopleFilter] = useState(searchParams.getAll("p").map(v => ({value: v, label: v})));
  const [droppedFilter, setDroppedFilter] = useState(strToBoolean(searchParams.get("d")));
  const [onlyUsers, setOnlyUsers] = useState(strToBoolean(searchParams.get("u")));
  const [onlyTodays, setOnlyTodays] = useState(strToBoolean(searchParams.get("t")));
  const [activeNow, setActiveNow] = useState(strToBoolean(searchParams.get("a")));


  const coordIds = Object.values(coordinators).map(g => g.map(c => c.user.id)).flat();
  const isCoordinator = coordIds.includes(userData.id);
  const [submissions, setSubmissions] = useState(subs);
  const [droppedHosts, setDroppedHosts] = useState([]);
  const [hosts, setHosts] = useState([]);


  const [latestSubChange, setLatestSubChange] = useState(0);
  const [latestHostChange, setLatestHostChange] = useState(0);

  // useEffect(() => {
  //
  //   parseQueryParams(searchParams);
  // }, []);

  useEffect(() => {
    let z = [];
    let s = [];
    let p = [];
    const checkParams = new URLSearchParams();
    if (sourceFilter.length) {
      SOURCE_OPTIONS.forEach((o, i) => {
        if (sourceFilter.includes(o)) {
          z.push(`${i}`);
          checkParams.append("z", `${i}`);
        }
      });
    }
    if (statusFilter.length) {
      SUB_STATE_OPTIONS.forEach((o, i) => {
        if (statusFilter.includes(o)) {
          s.push(`${i}`);
          checkParams.append("s", `${i}`);
        }
      });
    }
    if (peopleFilter.length) {
      peopleFilter.forEach((o) => {
        p.push(`${o.value}`);
        checkParams.append("p", `${o.value}`);
      });
    }
    let params = {z: z, s: s, p: p};
    if (droppedFilter) {
      params.d = "1";
      checkParams.append("d", "1");
    }
    if (onlyUsers) {
      params.u = "1";
      checkParams.append("u", "1");
    }
    if (onlyTodays) {
      params.t = "1";
      checkParams.append("t", "1");
    }
    if (activeNow) {
      params.a = "1";
      checkParams.append("a", "1");
    }
    if (checkParams.toString() !== searchParams.toString()) {
      setSearchParams(params);
    }
  }, [sourceFilter, statusFilter, droppedFilter, peopleFilter, activeNow, onlyUsers, onlyTodays]);

  useEffect(() => {
    const handler = () => {
      setTabVisible(!document.hidden);
    };
    document.addEventListener('visibilitychange', handler);
    return function cleanupListener() {
      document.removeEventListener('visibilitychange', handler);
    };
  }, []);

  useInterval(async () => {
    if (!tabVisible || UPDATE_LOOP_IS_PROCESSING) {
      return;
    }

    UPDATE_LOOP_IS_PROCESSING = true
    try {
      if (activeSub) {
        const latest = parseFloat(await getLatestHostTimestamp());

        if (latest > latestHostChange) {

          const response = await fetch(`/api/zasoby?since=${latestHostChange}`);
          const result = await response.json();

          const changedHosts = result.data;
          const changedIds = changedHosts.map(s => s.id);
          setHosts((currentHosts) => [
            ...currentHosts.filter(s => !changedIds.includes(s.id)),
            ...changedHosts.filter(h => shouldShowHost(h, userData.id))]
          );
          setLatestHostChange(latest);
        } else {

        }
      } else {
        // update submissions
        const latest = parseFloat(await getLatestSubId());

        if (latest > latestSubChange) {

          const response = await fetch(`/api/zgloszenia?since=${latestSubChange}`);
          const result = await response.json();

          const newSubs = result.data.submissions;
          const newSubsIds = newSubs.map(s => s.id);

          const regExp = /\s/g;
          newSubs.forEach(el => {
            el.created_raw = new Date(el.created_raw);
            el.phone_number_clean = el.phone_number.replace(regExp, '');
          });
          setSubmissions((cS) => [...cS.filter(s => !newSubsIds.includes(s.id)), ...newSubs]);
          // do latest for dropped
          setDroppedHosts(result.data.dropped);
          setLatestSubChange(latest);
        } else {

        }
      }
    } finally {
      UPDATE_LOOP_IS_PROCESSING = false
    }

  }, getRandomInt(1000, 1200));




  const clearActiveSub = () => setActiveSub(null);

  const subIsTaken = (sub, isActive = false, discard = false) => {

    let fields;
    if (isActive) {
      // no match found... we're clearing the status
      const status = discard ? "cancelled" : "new";
      fields = {"status": status, "matcher_id": null};
    } else {
      fields = {"status": "searching", "matcher_id": userData.id};
    }

    fetch(`/api/sub/update/${sub.id}`, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      headers: {
        'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')
      }, body: JSON.stringify({"fields": fields})
    }).then(response => response.json()).then(data => {

      toast(`${data.message}`, {type: data.status});
      if (!isActive) {
        setActiveSub(data.data);
      } else {
        setActiveSub(null);
      }

    }).catch((error) => {
      console.error('Error:', error);
    });
  };


  return <Routes>
    <Route exact path="/jazda" element={
      <>
        {/*<div className="ribbon">*/}
        {/*  Wszystkiego najlepszego dla naszych cudownych wolontariuszek ❤️*/}
        {/*  <i/>*/}
        {/*  <i/>*/}
        {/*  <i/>*/}
        {/*  <i/>*/}
        {/*</div>*/}
        <CoordinatorsHeader coordinators={coordinators} helped={helped} hide={Boolean(activeSub)}/>
        {activeSub ? <ResourceList initialResources={hosts}
                                   isLoading={latestHostChange === 0}
                                   user={userData} sub={activeSub} subHandler={subIsTaken}
                                   clearActiveSub={clearActiveSub}
        /> : <SubmissionList user={userData} subs={submissions} btnHandler={subIsTaken}
                             sourceFilter={sourceFilter} setSourceFilter={(v) => setSourceFilter(v)}
                             statusFilter={statusFilter}
                             isCoordinator={isCoordinator}
                             setStatusFilter={(v) => setStatusFilter(v)}
                             droppedHosts={droppedHosts}
                             isLoading={latestSubChange === 0}
                             userFilterValue={onlyUsers}
                             todayFilterValue={onlyTodays}
                             peopleFilter={peopleFilter}
                             setPeopleFilter={(v) => setPeopleFilter(v)}
                             setUserFilter={(v) => setOnlyUsers(v)}
                             setTodayFilter={(v) => setOnlyTodays(v)}
                             activeNow={activeNow} setActiveNow={(v) => setActiveNow(v)}
                             droppedFilter={droppedFilter} setDropped={(v) => setDroppedFilter(v)}
        />}
      </>}/>
  </Routes>;
};

ReactDOM.render(
    <BrowserRouter><App {...props} /></BrowserRouter>,
    // React.createElement(App, window.props),    // gets the props that are passed in the template
    window.react_mount,                                // a reference to the #react div that we render to
);
