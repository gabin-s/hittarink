'use strict'

const TRANSLATE_STRINGS = {
    "fr": [
        ["title", "Horaires patinoires Stockholm"],
        ["h1", "⛸️ à Stockholm"],
        [".subheading", "Vous trouverez ici les horaires hebdomadaires des patinoires de la ville de Stockholm."],
        [".legend > span:nth-of-type(1)", "avec crosse"],
        [".legend > span:nth-of-type(2)", "sans crosse"],
        [".legend > span:nth-of-type(3)", "glace partagée"],
    ],
}

function translate() {
    if(LOCALE == DEFAULT_LOCALE) return

    const language_code = LOCALE.split("-")[0]
    const l = TRANSLATE_STRINGS[language_code]
    if(l === undefined) return;
    
    document.documentElement.lang = language_code

    for(let [selector, text] of l) {
        const e = document.querySelector(selector)
        if(e !== null)
            e.innerText = text
    }
}
translate()

