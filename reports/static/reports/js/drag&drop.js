var dropZone = document.getElementById('dropZoneFiles');

// делаем drop зоны видимыми
function showDropZone() {
    dropZone.style.visibility = "visible";
}

// делаем drop зоны невидимыми
function hideDropZone() {
    dropZone.style.visibility = "hidden";
}

function allowDrag(e) {
    if (true) {
        e.dataTransfer.dropEffect = 'copy';
        e.preventDefault();
    }
}

// Файлы в upload
function handleDropFiles(e) {
    e.preventDefault();
    hideDropZone();

    const fileInput = document.getElementById('id_files');
    fileInput.files = e.dataTransfer.files;
}

var lastTarget = null; // Хер знает что, но без него drop зона работает как говно
// 1
window.addEventListener('dragenter', function(e) {
    lastTarget = e.target;
    showDropZone();
});

window.addEventListener('dragleave', function(e) {
 if(e.target === lastTarget || e.target === document)
    {
        hideDropZone();
    }
});


// 2
dropZone.addEventListener('dragenter', allowDrag);
dropZone.addEventListener('dragover', allowDrag);


// 3
dropZone.addEventListener('drop', handleDropFiles);
