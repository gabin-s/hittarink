'use strict'

const LOCALE = navigator.language || 'sv-se'

function getHM(d) {
    return new Date(d).toLocaleTimeString(LOCALE, {timeStyle: 'short'})
}

function getMonday(d) {
    d = new Date(d)
    var day = d.getDay(),
        diff = d.getDate() - day + (day == 0 ? -6:1) // adjust when day is sunday
    return new Date(d.setDate(diff))
}

function getDayName(i) {
    const d = new Date()
    d.setDate(-d.getDay() + i + 1)
    return d.toLocaleString(LOCALE, { weekday: "long" })
}

function get_ymd(d) {
    return d.getFullYear() + "-" + (d.getMonth()+1) + "-" + d.getDate()
}

function get_month_name(idx) {
    const objDate = new Date()
    objDate.setDate(1)
    objDate.setMonth(idx)

    return objDate.toLocaleString(LOCALE, { month: "long" })
}

function get_seconds_since_midnigh(d) {
    return d.getSeconds() + 60*d.getMinutes() + 3600*d.getHours()
}