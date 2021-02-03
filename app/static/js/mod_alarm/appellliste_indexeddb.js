var db = {};

function IndexedDB_open() {
    // This works on all devices/browsers, and uses IndexedDBShim as a final fallback
    var indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB || window.shimIndexedDB;

    var openDB = indexedDB.open("FWapp", 1);

    openDB.onupgradeneeded = function () {
        var db = {}
        db.result = openDB.result;
        db.store = db.result.createObjectStore("Presentlist", {keyPath: "id", autoIncrement: true});
    };
    openDB.onsuccess = function () {
        db = openDB.result;

        console.log("connection ok: " + db)
    }

    return openDB;
}

function IndexedDB_read(id, callback) {
    var transaction = db.transaction(["Presentlist"]);
    var objectStore = transaction.objectStore("Presentlist");
    var request = objectStore.get(id);

    request.onerror = function (event) {
        alert("Unable to retrieve daa from database!");
    };

    request.onsuccess = function (event) {
        callback(request.result)
    };

    request.oncomplete = function() {
        transaction.close()
    }
}

function IndexedDB_write(id, data, callback) {
    var request = db.transaction(["Presentlist"], "readwrite")
        .objectStore("Presentlist")
        .put(data);

    request.onsuccess = function (event) {
        callback(true)
    };

    request.onerror = function (event) {
        alert("Unable to add data ");
        callback(false)
    };

    request.oncomplete = function() {
        transaction.close()
    }
}

function getStoreIndexedDB(openDB) {

    db.result = openDB.result;
    db.tx = db.result.transaction("Presentlist", "readwrite");
    db.store = db.tx.objectStore("Presentlist");

    return true;
}

function saveIndexedDB(id, data) {
    var openDB = IndexedDB_open();

    openDB.onsuccess = function () {
        var db = getStoreIndexedDB(openDB);

        db.store.put({id: id, data: data});
    }

    return true;
}

function findIndexedDB(filesearch, callback) {
    return loadIndexedDB(null, callback, filesearch);
}

function loadIndexedDB(id) {
    var getData = db.store.get(id);

    return getData

}

function example() {
    var fileindex = ["name.last", "name.first"];
    saveIndexedDB(12345, {name: {first: "John", last: "Doe"}, age: 42});
    saveIndexedDB(67890, {name: {first: "Bob", last: "Smith"}, age: 35}, fileindex);

    loadIndexedDB(12345, callbackJohn);
    findIndexedDB(["Smith", "Bob"], callbackBob);
}

function callbackJohn(filedata) {
    console.log(filedata.name.first);
}

function callbackBob(filedata) {
    console.log(filedata.name.first);
}