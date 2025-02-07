import moment from "moment"

export function dateFormat(row:any, column:any) {
    const date = row[column.property];
    if (date == undefined)
        return ""

    return moment(date).format("YYYY-MM-DD HH:mm:ss")
}

export function getTimeInterval(target){  // target is a representation of ISO 8601 format, e.g: 2023-04-24T06:13:30.447809Z
    const now = new Date().getTime();
    const targetTime = new Date(target).getTime();
    return Math.floor((now - targetTime)/1000);
}

export function dateTransform(gmtDate){ //gmtDate is a representation of GMT format, e.g：Wed Apr 05 2023 00:00:00 GMT+0800， target: 2023-04-20
    const date = new Date(gmtDate);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const dateString = `${year}-${month}-${day}`;
    return dateString;
}

export function calculatePreviousDate(inputDate, minusValue){ // inputDate: like 2023-04-20   minusValue: like 3
  const date = new Date(inputDate);
  date.setDate(date.getDate() - minusValue);
  // convert to this format yyyy-mm-dd
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}