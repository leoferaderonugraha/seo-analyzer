var wordCount = $('#wordCount');
var pageTitle = $('#pageTitle');
var metaDescription = $('#metaDescription');
var missingImgAlt = $('#missingImgAlt');
var internalLinks = $('#internalLinks');
var externalLinks = $('#externalLinks');
var brokenLinks = $('#brokenLinks');
var inputUrl = $('#inputUrl');
var statusMsg = $('#statusMsg');
var keywordsOnPage = $('#keywordsOnPage');
var sitemap = $('#sitemap');

var socket = new WebSocket('ws://localhost:8888');

function sendRequest() {
    let data = inputUrl.val()
    statusMsg.html('Waiting for the result...');
    socket.send(data)
}


function updateData(element, value) {
    pos = element.html().indexOf(':');
    if (value !== "") {
        element.html(element.html().substr(0, pos + 2) + value);
    } else {
        element.html(element.html().substr(0, pos + 2) + 'null');
    }
}


socket.addEventListener('close', function() {
    console.log('connection closed');
})

socket.addEventListener('open', function() {
    data = {'id': Math.floor(Math.random() * 100)}
    socket.send(JSON.stringify(data))
})

socket.addEventListener('message', function(data) {
    statusMsg.html('')

    parsedData = JSON.parse(data.data);
    updateData(pageTitle, parsedData.page_title);
    updateData(wordCount, parsedData.word_count);
    updateData(metaDescription, parsedData.meta_description);
    updateData(keywordsOnPage, parsedData.keywords.join(' | '));
    updateData(missingImgAlt, parsedData.missing_img_alt);
    updateData(internalLinks, parsedData.internal_links);
    updateData(externalLinks, parsedData.external_links);
    updateData(brokenLinks, parsedData.broken_links);
    updateData(sitemap, parsedData.sitemap);
})
