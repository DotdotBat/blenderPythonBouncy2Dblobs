from chatGptCode import HashGrid, Coordinate2D

def run_test():
    # Step 1: Initialize a HashGrid
    grid = HashGrid(width=100, height=100, cell_size=10)

    # Step 2: Create a Coordinate2D Object
    point = Coordinate2D(x=5, y=5)
    point2 = Coordinate2D(x=16, y=11)
    # Step 3: Register the Point via the Client
    client = grid.create_client(point)
    client2 = grid.create_client(point2)

    # Step 4: Retrieve the Point via the Hash Grid
    same_cell_query_result = len(grid.query(x=point.x, y=point.y, radius=5))
    print("Same Cell Query Result:", same_cell_query_result)

    # Step 5: Query for the Point in a Neighboring Cell
    neighboring_cell_query_result = len(grid.query(x=15, y=15, radius=4))
    print("Neighboring Cell Query Result:", neighboring_cell_query_result)

    # Step 6: Move the Point and Check Its Position
    point.x = 15
    point.y = 15
    point2.x = 40
    point2.y = 30
    client.update()
    client2.update()
    new_position_query_result = len(grid.query(x=point.x, y=point.y, radius=5))
    print("New Position Query Result:", new_position_query_result)