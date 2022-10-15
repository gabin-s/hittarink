'use strict'

const ONE_DAY_S  = 3600*24
const ONE_DAY_MS = ONE_DAY_S*1000
const COMMENTS_CSS_CLASSES = {
    "delad is":    "legend_delad",// red-greed stripes
    "med klubba":  "legend_med",  // red
    "utan klubba": "legend_utan", // green
}
const COMMENTS_CSS_CLASS_DEFAULT = 'legend_default' // grey

let schedules_data = []
const placenames = JSON.parse('["Farsta IP", "Grimsta IP", "Gubb\\u00e4ngens IP (Bandyhallen)", "Gubb\\u00e4ngens IP (Bandybana)", "Husby ishall", "K\\u00e4rrtorps IP", "M\\u00e4larh\\u00f6jdens IP", "Sp\\u00e5nga IP (Bandyplanen)", "Sp\\u00e5nga IP (Ishallen)", "Stora Mossens IP (A-hallen)", "Stora Mossens IP (B-hallen (HCL-hallen))", "Zinkensdamms IP (Ishallen)", "Zinkensdamms IP (Bandyplanen)", "\\u00d6stermalms IP (Ishallen)", "\\u00d6stermalms IP (Rundbana)", "\\u00d6stermalms IP (Halvm\\u00e5ne, n\\u00e4rmast Liding\\u00f6v\\u00e4gen)"]')

// keep track of the day container in the DOM
const event_containers = new Array()
const select           = document.getElementById('place')
const overlay_noevents = document.getElementById('overlay_noevents')
const alert_element    = document.getElementsByClassName('alert')[0]
const week_indicator   = document.getElementById('week_indicator')

let startOfWeek, endOfWeek

function init_select(select) {
    // create options in the dropdown
    const createOption = function(parent, content, value) {
        const option = document.createElement('option')
        option.value     = value
        option.innerText = content
        parent.appendChild(option)
    }

    for(let i = 0; i < placenames.length; i++) {
        let placename = placenames[i]
        createOption(select, placename, i)
    }
}

function init() {
    // contains the days
    const calendar = document.getElementById('calendar_container')

    startOfWeek = getMonday(new Date())

    // create all 7 day containers
    for(let i = 0; i < 7; i++) {
        // contains the events
        const event_container = document.createElement('div')
        event_container.classList.add('event_container')
        event_containers.push(event_container)

        // a column of the calendar
        const day = document.createElement('div')
        day.classList.add('column')

        // name of the day
        const day_tag = document.createElement('span')
        day_tag.innerText = getDayName(i)

        day.appendChild(day_tag)
        day.appendChild(event_container)

        calendar.appendChild(day)
    }

    init_select(select)
    
    // add event listeners
    select.addEventListener('change', update_calendar)
    document.addEventListener('keydown', onKeyDown)

    onWeekUpdated()
}

function update_data(data) {
    schedules_data = data
    update_calendar()
}

function show_error(error) {
    alert_element.children[1].innerText = 'An error occured: ' + error
    alert_element.style.display = 'block'
}

function fetch_data(d) {
    // get the data for this week
    const url = 'data/' + get_ymd(d) + ".json"
    
    const onData = function(data) {
        schedules_data = data
        update_calendar()
    }

    const onSuccess = function(res) {
        if(res.status == 200)
            res.json().then(onData).catch(onError)
        else if(res.status == 404)
            onData([])
        else
            onError()
    }

    const onError = function(e) {
        show_error('unable to load data, please check connectivity')
    }

    fetch(url)
        .then(onSuccess)
        .catch(onError)
}

function onWeekUpdated() {
    endOfWeek = new Date(startOfWeek)
    endOfWeek.setDate(endOfWeek.getDate() + 7)

    const monthA = startOfWeek.getMonth()
    const monthB = endOfWeek.getMonth()

    const dayA = startOfWeek.getDate()
    const dayB = new Date(endOfWeek - 1).getDate()
    
    let text
    if(monthA == monthB)
        text = dayA + '-' + dayB + ' ' + get_month_name(monthA)
    else
        text = dayA + ' ' + get_month_name(monthA) + '-' + dayB + ' ' + get_month_name(monthB)

    week_indicator.innerText = text

    fetch_data(startOfWeek)
}

function seek_select_option(incr) {
    // next option in select
    var i = select.selectedIndex + incr

    if(i < 0 || i >= select.options.length) return
    select.options[i].selected = true
    
    update_calendar()
}

function onKeyDown(e) {
    switch(e.key) {
        case "ArrowRight":
            week_next()
            break
        case "ArrowLeft":
            week_previous()
            break
        case "ArrowUp":
            seek_select_option(-1)
            break
        case "ArrowDown":
            seek_select_option(1)
            break
        default:
            return
    }

    e.preventDefault()
}

function incr_week(i) {
    startOfWeek.setDate(startOfWeek.getDate() + i * 7)

    onWeekUpdated()
}

function week_previous() { incr_week(-1) }
function week_next() { incr_week(1) }

function update_calendar() {

    const schedules = schedules_data.filter(
        e => e[0] == select.value // filter by place + subplace
    )

    // clear all previous schedules
    for(const c of event_containers) {
        c.innerHTML = ''
    }

    for(const schedule of schedules) {
        const t_start = new Date(schedule[1])
        const t_end   = new Date(schedule[2])
        
        let i = (t_start.getDay() - 1)
        if(i == -1) i = 6 // correct for Sunday

        // height of the block (percentage of container)
        const height  = 100 * (t_end - t_start) / ONE_DAY_MS
        const css_top = 100 *  get_seconds_since_midnigh(t_start) / ONE_DAY_S
        
        const e = document.createElement('div')
        e.classList.add(COMMENTS_CSS_CLASSES[schedule[3]] || COMMENTS_CSS_CLASS_DEFAULT)
        e.classList.add('event')

        e.style.height = height + '%'
        e.style.top    = css_top + '%'
        e.innerText = getHM(t_start) + '-' + getHM(t_end)
    
        event_containers[i].appendChild(e)
    }

    overlay_noevents.hidden = schedules.length != 0
}

init()