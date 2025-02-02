import { t } from "i18next";
import React, {useEffect, useRef, useState} from "react";
import { useTranslation } from 'react-i18next';

export const EditableField = ({value, classes = '', noEditClasses = '', onRename}) => {

  const [editable, setEditable] = useState(false);
  const [currentValue, setCurrentValue] = useState(value);
  const inputRef = useRef(null);
  const { t } = useTranslation('backoffice');

  useEffect(() => {
    if (editable) {
      inputRef.current.focus();
    } else if (currentValue !== value) {
      onRename(currentValue);
    }
  }, [editable]);

  const keyUpHandler = (event) => {
    if (event.keyCode === 13) {  // enter
      event.preventDefault();
      inputRef.current.blur();
    }
  };

  return (editable ? <div className={classes} style={{display: editable ? "" : "none"}}
                          onBlur={() => setEditable(false)}>
            <textarea className="form-control" value={currentValue} ref={inputRef}
                      placeholder={t('add_note')}
                      onChange={(e) => setCurrentValue(e.target.value)}
                      onKeyDown={keyUpHandler}/></div> : <div className="rename-input" onClick={() => setEditable(true)}>
    <span className={value ? "" : "text-muted"}>{value.trim() || t('click_to_add_note')}</span>
  </div>);

};

export function LoadingSpinner() {
  return <div style={{margin: "0 auto", width: "fit-content"}}>
    <div className="spinner-border text-center mt-5" role="status">
      <span className="visually-hidden">{t('loading')}</span>
    </div>
  </div>;
}

export function PrepareSearchQuery(query) {
  return query.replace(/\s+/g, '').toLowerCase();
}

export function ResourceAsStringForSearch(r) {
    var no_whitespaces = Object.values(r).map((e) => String(e).replace(/\s+/g, ''));
    return no_whitespaces.join(' ').toLowerCase();
}
