import titles from './titles.json' with { type: 'json' }

const resultsBox = document.getElementById("searchBox")
const searchInput = document.getElementById("searchInput")

showAll()

searchInput.addEventListener("input", (e) => {
    const searchText = e.target.value   

    if (searchText.length === 0) {
        showAll()
        return
    }

    const results = fuzzysort.go(searchText, titles, {
        threshold: 0.5
    }).map(x => x.target)

    resultsBox.innerHTML = ""

    for (const title of results) {
        const newRow = document.createElement("a")
        newRow.href = "/" + title
        newRow.textContent = title
        newRow.classList.add("searchItem")
        resultsBox.appendChild(newRow)
    }
})

function showAll() {
    titles.sort()

    resultsBox.innerHTML = ""

    for (const title of titles) {
        const newRow = document.createElement("a")
        newRow.href = "/" + title
        newRow.textContent = title
        newRow.classList.add("searchItem")
        resultsBox.appendChild(newRow)
    }
}