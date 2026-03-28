function selectCategory(category) {
    document.getElementById("selectedCategory").innerText = category;

    let formHTML = "";

    if (category === "Education") {
        formHTML = `
            <form action="/upload" method="POST" enctype="multipart/form-data">
                <input type="text" name="title" placeholder="Chapter Name" required>
                <input type="number" name="time" placeholder="Time spent (minutes)" required>
                <input type="file" name="file" required>

                <button>Upload & Learn</button>
            </form>
        `;
    } 
    else if (category === "Health") {
        formHTML = `
            <form action="/add" method="POST">
                <input type="hidden" name="category" value="Health">

                <input type="text" name="title" placeholder="Reminder Type (e.g. Drink Water)" required>
                <textarea name="details" placeholder="Message"></textarea>

                <button>Add Reminder</button>
            </form>
        `;
    }

    document.getElementById("formSection").innerHTML = formHTML;
}