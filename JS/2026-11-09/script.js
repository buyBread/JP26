const product_key = "product_list";
const cart_key    = "cart_list";

const product_form = document.getElementById("product-form");
const input_id     = product_form.querySelector("#id");
const input_name   = product_form.querySelector("#name");
const input_count  = product_form.querySelector("#count");

const cart_form  = document.getElementById("cart-form");
const input_cart = document.getElementById("cart-id");

const product_table = document.getElementById("product-table");
const cart_table    = document.getElementById("cart-table");
const table_all     = document.getElementById("product-table-all");
const table_cart    = document.getElementById("cart-table-items");

const btn_add      = document.getElementById("btn-add");
const btn_edit     = document.getElementById("btn-edit");
const btn_rm       = document.getElementById("btn-rm");
const btn_cart_add = document.getElementById("btn-cart-add");

let product_list = [];
let cart_list    = [];
let selected_id  = null;

const message_box = document.createElement("p");
product_form.after(message_box);

const cart_message_box = document.createElement("p");
cart_form.after(cart_message_box);

function show_message(message, error = false, target = message_box) {
    target.textContent = message;
    target.style.color = error ? "#923535" : "#3d6e3d";
}

function load_data() {
    try {
        const stored_products = localStorage.getItem(product_key);
        const stored_cart = localStorage.getItem(cart_key);

        if (stored_products === null && stored_cart !== null) {
            // Older versions stored the product catalog under "cart_list".
            product_list = JSON.parse(stored_cart);
            if (!Array.isArray(product_list)) product_list = [];
            cart_list = [];
            localStorage.setItem(product_key, JSON.stringify(product_list));
            localStorage.setItem(cart_key, JSON.stringify(cart_list));
        } else {
            product_list = stored_products ? JSON.parse(stored_products) : [];
            cart_list = stored_cart ? JSON.parse(stored_cart) : [];
            if (!Array.isArray(product_list)) product_list = [];
            if (!Array.isArray(cart_list)) cart_list = [];
        }

        // Only keep cart entries that still exist in the product catalog.
        cart_list = cart_list.filter(item => find_product(item.id));
    } catch (error) {
        product_list = [];
        cart_list = [];
        show_message("Failed to load saved data.", true);
    }

    display_all();
    display_cart();
}

function save_data() {
    try {
        localStorage.setItem(product_key, JSON.stringify(product_list));
        localStorage.setItem(cart_key, JSON.stringify(cart_list));
        
        return true;
    } catch (error) {
        show_message("Failed to save data.", true);

        return false;
    }
}

function validate_input() {
    const id       = input_id.value.trim();
    const name     = input_name.value.trim();
    const quantity = input_count.value.trim();

    if (!id || !name || !quantity) {
        show_message("All fields must be filled!", true);

        return null;
    }

    if (!/^\d+$/.test(id)) {
        show_message("Product code must contain only numbers!", true);

        return null;
    }

    if (!/^\d+$/.test(quantity) || Number(quantity) <= 0) {
        show_message("Quantity must be a positive whole number!", true);

        return null;
    }

    return { id, name, quantity };
}

function find_product(id) {
    return product_list.find(product => String(product.id) === String(id));
}

function clear_form() {
    product_form.reset();
    input_id.readOnly = false;
    selected_id = null;
}

function create_row(product) {
    const row = document.createElement("tr");

    for (const value of [product.id, product.name, product.quantity]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
    }

    return row;
}

function select_product(id) {
    const product = find_product(id);
    
    if (!product)
        return;

    selected_id = String(product.id);
    input_id.value = product.id;
    input_name.value = product.name;
    input_count.value = product.quantity;
    input_id.readOnly = true;

    display_all();
    show_message("Product selected for editing or deletion.");
}

function display_all() {
    table_all.replaceChildren();

    product_list.forEach(product => {
        const row = create_row(product);
        row.tabIndex = 0;
        row.setAttribute("role", "button");
        row.setAttribute("aria-label", `Select ${product.name}`);
        row.classList.toggle("selected", String(product.id) === selected_id);
        row.addEventListener("click", () => select_product(product.id));
        row.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                select_product(product.id);
            }
        });
        table_all.appendChild(row);
    });

    product_table.hidden = product_list.length === 0;
}

function display_cart() {
    table_cart.replaceChildren();

    cart_list.forEach(product => {
        const row = create_row(product);
        const action_cell   = document.createElement("td");
        const remove_button = document.createElement("button");
         
        remove_button.type = "button";
        remove_button.textContent = "Remove";
        remove_button.addEventListener("click", () => remove_from_cart(product.id));
        action_cell.appendChild(remove_button);
        row.appendChild(action_cell);
        table_cart.appendChild(row);
    });

    cart_table.hidden = cart_list.length === 0;
}

function insert_product() {
    if (selected_id !== null) {
        show_message("Finish editing or cancel the selection first!", true);

        return;
    }

    const product = validate_input();
    if (!product) return;

    if (find_product(product.id)) {
        show_message("A product with this code already exists!", true);

        return;
    }

    product_list.push(product);
    if (!save_data()) {
        product_list.pop();

        return;
    }

    clear_form();
    display_all();
    show_message("Product inserted successfully!");
}

function edit_product() {
    if (selected_id === null) {
        show_message("Click a product row to select it first!", true);

        return;
    }

    const updated_product = validate_input();

    if (!updated_product)
        return;

    const index = product_list.findIndex(product => String(product.id) === selected_id);
    if (index === -1) {
        show_message("Product not found!", true);

        return;
    }

    const previous_product = product_list[index];
    const previous_cart = [...cart_list];

    product_list[index] = updated_product;
    cart_list = cart_list.map(item =>
        String(item.id) === selected_id ? { ...updated_product } : item
    );

    if (!save_data()) {
        product_list[index] = previous_product;
        cart_list = previous_cart;

        return;
    }

    clear_form();
    display_all();
    display_cart();
    show_message("Product updated successfully!");
}

function delete_product() {
    const id = selected_id || input_id.value.trim();

    if (!id) {
        show_message("Select a product or enter its code to delete!", true);

        return;
    }

    if (!find_product(id)) {
        show_message("Product not found!", true);

        return;
    }

    const previous_products = [...product_list];
    const previous_cart = [...cart_list];

    product_list = product_list.filter(product => String(product.id) !== String(id));
    cart_list = cart_list.filter(product => String(product.id) !== String(id));

    if (!save_data()) {
        product_list = previous_products;
        cart_list = previous_cart;

        return;
    }

    clear_form();
    display_all();
    display_cart();
    show_message("Product deleted from the catalog and cart.");
}

function add_to_cart() {
    const id = input_cart.value.trim();

    if (!/^\d+$/.test(id)) {
        show_message("Enter a numeric product code!", true, cart_message_box);

        return;
    }

    const product = find_product(id);
    if (!product) {
        show_message("Product not found!", true, cart_message_box);

        return;
    }

    if (cart_list.some(item => String(item.id) === id)) {
        show_message("Product is already in the cart!", true, cart_message_box);

        return;
    }

    cart_list.push({ ...product });

    if (!save_data()) {
        cart_list.pop();
        show_message("Failed to save cart.", true, cart_message_box);

        return;
    }

    cart_form.reset();
    display_cart();
    show_message("Product added to cart!", false, cart_message_box);
}

function remove_from_cart(id) {
    const previous_cart = [...cart_list];

    cart_list = cart_list.filter(product => String(product.id) !== String(id));

    if (!save_data()) {
        cart_list = previous_cart;
        show_message("Failed to save cart.", true, cart_message_box);

        return;
    }

    display_cart();
    show_message("Product removed from cart.", false, cart_message_box);
}

product_form.addEventListener("submit", event => {
    event.preventDefault();
    
    if (selected_id === null)
        insert_product();
    else
        edit_product();
});

cart_form.addEventListener("submit", event => {
    event.preventDefault();
    add_to_cart();
});

btn_add .addEventListener("click", insert_product);
btn_edit.addEventListener("click", edit_product);
btn_rm  .addEventListener("click", delete_product);

btn_cart_add.addEventListener("click", add_to_cart);

load_data();