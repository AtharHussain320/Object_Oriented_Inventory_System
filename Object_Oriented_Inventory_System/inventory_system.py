import json
from pathlib import Path


DATA_FILE = Path("inventory.json")



# CATEGORY CLASS

class Category:
    """Represents a product category."""

    def __init__(self, name, description=""):
        self.name = name.strip().title()
        self.description = description.strip()

    def to_dict(self):
        """Convert category into a dictionary."""

        return {
            "name": self.name,
            "description": self.description
        }



# PRODUCT CLASS

class Product:
    """Represents an inventory product."""

    def __init__(
        self,
        product_id,
        name,
        category,
        price,
        quantity,
        reorder_level=5
    ):
        self.product_id = product_id
        self.name = name.strip()
        self.category = category.strip().title()
        self.price = float(price)
        self.quantity = int(quantity)
        self.reorder_level = int(reorder_level)

    def update(self, name=None, price=None, quantity=None):
        """Update selected product information."""

        if name:
            self.name = name.strip()

        if price is not None:
            self.price = float(price)

        if quantity is not None:
            self.quantity = int(quantity)

    def is_low_stock(self):
        """Return True when stock reaches reorder level."""

        return self.quantity <= self.reorder_level

    def to_dict(self):
        """Convert product into a dictionary."""

        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
            "reorder_level": self.reorder_level
        }



# INVENTORY CLASS

class Inventory:
    """Manages products and inventory operations."""

    def __init__(self):
        self.products = {}
        self.categories = {}


    # CATEGORY OPERATIONS

    def add_category(self, name, description=""):
        """Add a new category."""

        name = name.strip().title()

        if not name:
            raise ValueError("Category name cannot be empty.")

        if name in self.categories:
            raise ValueError("Category already exists.")

        self.categories[name] = Category(
            name,
            description
        )


    # PRODUCT OPERATIONS

    def add_product(
        self,
        product_id,
        name,
        category,
        price,
        quantity,
        reorder_level=5
    ):
        """Add a product to inventory."""

        if product_id in self.products:
            raise ValueError("Product ID already exists.")

        if not name.strip():
            raise ValueError("Product name cannot be empty.")

        if price <= 0:
            raise ValueError("Price must be greater than zero.")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        if category.strip().title() not in self.categories:
            raise ValueError(
                f"Category '{category}' does not exist."
            )

        product = Product(
            product_id,
            name,
            category,
            price,
            quantity,
            reorder_level
        )

        self.products[product_id] = product

    def update_product(
        self,
        product_id,
        name=None,
        price=None,
        quantity=None
    ):
        """Update an existing product."""

        if product_id not in self.products:
            raise ValueError("Product not found.")

        if price is not None and price <= 0:
            raise ValueError("Price must be greater than zero.")

        if quantity is not None and quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        self.products[product_id].update(
            name,
            price,
            quantity
        )

    def remove_product(self, product_id):
        """Remove a product."""

        if product_id not in self.products:
            raise ValueError("Product not found.")

        del self.products[product_id]

    def search(self, keyword):
        """Search products by name or category."""

        keyword = keyword.lower().strip()

        return [
            product
            for product in self.products.values()
            if (
                keyword in product.name.lower()
                or keyword in product.category.lower()
            )
        ]

    
    # REPORTING

    def total_inventory_value(self):
        """Calculate total value of inventory."""

        return sum(
            product.price * product.quantity
            for product in self.products.values()
        )

    def low_stock_products(self):
        """Return products that need restocking."""

        return [
            product
            for product in self.products.values()
            if product.is_low_stock()
        ]

    def category_summary(self):
        """Calculate inventory summary by category."""

        summary = {}

        for product in self.products.values():

            category = product.category

            if category not in summary:
                summary[category] = {
                    "products": 0,
                    "units": 0,
                    "value": 0
                }

            summary[category]["products"] += 1
            summary[category]["units"] += product.quantity
            summary[category]["value"] += (
                product.price * product.quantity
            )

        return summary

    
    # PERSISTENCE

    def save(self):
        """Save inventory to JSON."""

        data = {
            "categories": [
                category.to_dict()
                for category in self.categories.values()
            ],
            "products": [
                product.to_dict()
                for product in self.products.values()
            ]
        }

        try:
            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4
                )

            return True

        except OSError as error:
            print(f"Could not save inventory: {error}")
            return False

    def load(self):
        """Load inventory from JSON."""

        if not DATA_FILE.exists():
            return

        try:
            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.categories.clear()
            self.products.clear()

            for category in data.get("categories", []):

                self.add_category(
                    category["name"],
                    category.get("description", "")
                )

            for product in data.get("products", []):

                self.add_product(
                    product["product_id"],
                    product["name"],
                    product["category"],
                    product["price"],
                    product["quantity"],
                    product.get("reorder_level", 5)
                )

        except json.JSONDecodeError:
            print(
                "Warning: inventory.json is corrupted."
            )

        except (KeyError, TypeError, ValueError) as error:
            print(
                f"Warning: invalid inventory data: {error}"
            )

        except OSError as error:
            print(
                f"Unable to read inventory: {error}"
            )



# DISPLAY FUNCTIONS

def display_products(products):
    """Display products in a readable table."""

    if not products:
        print("\nNo products found.")
        return

    print("\n" + "=" * 90)
    print("INVENTORY")
    print("=" * 90)

    print(
        f"{'ID':<8}"
        f"{'Product':<24}"
        f"{'Category':<18}"
        f"{'Price':>12}"
        f"{'Qty':>10}"
        f"{'Status':>12}"
    )

    print("-" * 90)

    for product in products:

        status = (
            "LOW STOCK"
            if product.is_low_stock()
            else "Available"
        )

        print(
            f"{product.product_id:<8}"
            f"{product.name[:22]:<24}"
            f"{product.category:<18}"
            f"Rs. {product.price:>7.2f}"
            f"{product.quantity:>10}"
            f"{status:>12}"
        )

    print("=" * 90)


def display_report(inventory):
    """Display inventory summary report."""

    print("\n" + "=" * 55)
    print("INVENTORY SUMMARY REPORT")
    print("=" * 55)

    print(
        f"Total products : {len(inventory.products)}"
    )

    total_units = sum(
        product.quantity
        for product in inventory.products.values()
    )

    print(f"Total units    : {total_units}")

    print(
        f"Inventory value: "
        f"Rs. {inventory.total_inventory_value():,.2f}"
    )

    low_stock = inventory.low_stock_products()

    print(
        f"Low-stock items: {len(low_stock)}"
    )

    print("\nCategory Breakdown")
    print("-" * 55)

    for category, data in inventory.category_summary().items():

        print(
            f"{category:<18}"
            f"Products: {data['products']:<4}"
            f"Units: {data['units']:<5}"
            f"Value: Rs. {data['value']:,.2f}"
        )



# SAMPLE DATA

def create_demo_inventory():
    """Create initial demo data for first-time execution."""

    inventory = Inventory()

    inventory.add_category(
        "Electronics",
        "Electronic devices and accessories"
    )

    inventory.add_category(
        "Stationery",
        "Office and study supplies"
    )

    inventory.add_category(
        "Accessories",
        "Computer and mobile accessories"
    )

    inventory.add_product(
        "P001",
        "Wireless Mouse",
        "Accessories",
        1850,
        18
    )

    inventory.add_product(
        "P002",
        "Mechanical Keyboard",
        "Electronics",
        6500,
        7
    )

    inventory.add_product(
        "P003",
        "USB-C Cable",
        "Accessories",
        950,
        4
    )

    inventory.add_product(
        "P004",
        "Notebook",
        "Stationery",
        450,
        25
    )

    inventory.add_product(
        "P005",
        "Desk Lamp",
        "Electronics",
        3200,
        3
    )

    return inventory



# MAIN APPLICATION

def main():

    print("\n" + "=" * 60)
    print("        SMART INVENTORY MANAGEMENT SYSTEM")
    print("=" * 60)

    inventory = Inventory()

    if DATA_FILE.exists():
        inventory.load()
        print("✓ Existing inventory loaded.")

    else:
        inventory = create_demo_inventory()
        inventory.save()
        print("✓ Demo inventory created.")

    while True:

        print("\n" + "-" * 45)
        print("MAIN MENU")
        print("-" * 45)

        print("1. View Inventory")
        print("2. Search Product")
        print("3. Add Product")
        print("4. Update Product")
        print("5. Remove Product")
        print("6. Low Stock Report")
        print("7. Inventory Summary")
        print("0. Exit")

        choice = input("\nSelect option: ").strip()

        
        # VIEW

        if choice == "1":

            display_products(
                list(inventory.products.values())
            )

        
        # SEARCH

        elif choice == "2":

            keyword = input(
                "Enter product/category to search: "
            )

            results = inventory.search(keyword)

            display_products(results)

        
        # ADD

        elif choice == "3":

            try:

                product_id = input(
                    "Product ID: "
                ).strip()

                name = input(
                    "Product name: "
                ).strip()

                category = input(
                    "Category: "
                ).strip()

                price = float(
                    input("Price: ")
                )

                quantity = int(
                    input("Quantity: ")
                )

                inventory.add_product(
                    product_id,
                    name,
                    category,
                    price,
                    quantity
                )

                inventory.save()

                print("✓ Product added successfully.")

            except ValueError as error:

                print(f"✗ {error}")

        
        # UPDATE

        elif choice == "4":

            product_id = input(
                "Product ID to update: "
            ).strip()

            if product_id not in inventory.products:

                print("✗ Product not found.")
                continue

            try:

                product = inventory.products[product_id]

                print(
                    f"Current product: "
                    f"{product.name}"
                )

                name = input(
                    "New name (Enter to keep): "
                ).strip()

                price_text = input(
                    "New price (Enter to keep): "
                ).strip()

                quantity_text = input(
                    "New quantity (Enter to keep): "
                ).strip()

                price = (
                    float(price_text)
                    if price_text
                    else None
                )

                quantity = (
                    int(quantity_text)
                    if quantity_text
                    else None
                )

                inventory.update_product(
                    product_id,
                    name or None,
                    price,
                    quantity
                )

                inventory.save()

                print("✓ Product updated.")

            except ValueError as error:

                print(f"✗ {error}")

        
        # REMOVE

        elif choice == "5":

            product_id = input(
                "Product ID to remove: "
            ).strip()

            try:

                inventory.remove_product(product_id)
                inventory.save()

                print("✓ Product removed.")

            except ValueError as error:

                print(f"✗ {error}")

        # ----------------------------------------------------
        # LOW STOCK
        # ----------------------------------------------------

        elif choice == "6":

            low_stock = inventory.low_stock_products()

            print("\n⚠ LOW STOCK PRODUCTS")

            display_products(low_stock)

    
        # REPORT

        elif choice == "7":

            display_report(inventory)

    
        # EXIT

        elif choice == "0":

            inventory.save()

            print(
                "\n✓ Inventory saved successfully."
            )

            print(
                "Thank you for using Smart Inventory System!"
            )

            break

        else:

            print(
                "✗ Invalid option. Please try again."
            )


if __name__ == "__main__":
    main()