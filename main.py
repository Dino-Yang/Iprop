import pymongo


# used to edit the list of recommended games
def recHelper(helpList, developer, name):
    maxGames = 5
    # remove the game itself from the recommended games list
    for x in helpList:
        if x["name_lower"] == name:
            helpList.remove(x)
    # games from the same developer get put at the beginning of the list
    for x in helpList:
        if x["developer"] == developer:
            helpList.remove(x)
            helpList.insert(0, x)
    # deletes every game between index 5 till the last game
    # we do this so only the top 5 recommendations get printed out
    del helpList[maxGames:len(helpList)]
    return helpList


# used to find recommendations of a given game
def recGame(game):
    developer = None
    name = None
    genre2 = None
    genre1 = None
    for key, value in game.items():
        if key == "name_lower":
            name = value
        if key == "genre1":
            genre1 = value
        if key == "genre2":
            genre2 = value
        if key == "developer":
            developer = value
    # finds games that have the same genres
    helpList = list(collection.find({"$or": [
        {"genre1": {"$in": [genre1, genre2]}},
        {"genre2": {"$in": [genre1, genre2]}}
    ]}))
    print()
    helpList = recHelper(helpList, developer, name)
    searchHelpChange(helpList, "search")


# prints out a list of games to pick from nicely
def printSearch(game, i):
    for key, value in game.items():
        if key == "_id":
            print("[" + str(i) + "]Name: " + value)


# used to print out a game from the database nicely
def printGame(game):
    print()
    for key, value in game.items():
        if key == "_id":
            print("Name: " + value)
        if key == "genre1":
            print("Genre1: " + value)
        if key == "genre2":
            print("Genre2: " + value)
        if key == "developer":
            print("Developer: " + value)
        if key == "year":
            print("Released in: " + str(value))
        if key == "rating":
            print("Rating: " + str(value))
    print()


def changeMenu():
    print("Would you like to change this game?")
    print("[1]Yes")
    print("[2]Go back to main menu")


def recMenu():
    print("[1]See recommendations")
    print("[2]Go back to main menu")


def menu():
    print("[1]Search Game")
    print("[2]Add Game")
    print("[3]Delete Game")
    print("[4]Change Game")
    print("[0]Close program")


# helper function used to make code more readable
# prints out result and lets the user pick one of the games.
# Given the 'function', we either let the user choose to get
# recs for the chosen game or we let the user change
# an attribute of the chosen game
def searchHelpChange(result, function):
    chosenGame = None
    i = 0
    print()
    for doc in result:
        printSearch(doc, i + 1)
        i += 1
    print()
    print("Please choose a game, or enter 0 to go back")
    option = choice()
    while option != 0:
        if i >= option > 0:
            printGame(result[option - 1])
            chosenGame = result[option - 1]
            if function == "search":
                recMenu()
            else:
                changeMenu()
            break
        else:
            print("Thats not a valid option")
        option = choice()
    if option == 0:
        return
    option = choice()
    if option == 1:
        if function == "search":
            recGame(chosenGame)
        else:
            changeGameHelp(chosenGame["_id"])
    elif option == 2:
        return
    else:
        print("Thats not a valid option")


# used to search for a game in the database
def searchName():
    gameName = input("Name of game?\n")
    answer = collection.find_one({"name_lower": gameName.lower()})
    if answer is None:
        # checks whether there are games in the database that have
        # gameName as a substring and puts them into a list:result
        answer = collection.find({"name_lower": {"$regex": gameName.lower()}})
        result = list(answer)
        # if there are games in the database that match gameName,
        # print them out
        if len(result) != 0:
            print("Did you mean?")
            searchHelpChange(result, "search")
        else:
            print("No game matches that name!")
    else:
        printGame(answer)
        recMenu()
        option = choice()
        if option == 1:
            recGame(answer)
        elif option == 2:
            return
        else:
            print("Thats not a valid option")


# used to add a game into the database
def addGame():
    gameName = input("Name?\n")
    genre1 = input("Genre 1?\n")
    genre2 = input("Genre 2?\n")
    developer = input("Developer?\n")
    rating = input("Rating?\n")
    year = input("Release year?\n")
    collection.insert_one(
        {"_id": gameName, "name_lower": gameName.lower(), "genre1": genre1,
         "genre2": genre2, "developer": developer, "rating": rating,
         "year": year})


# changeGameOption makes changeGameHelp able to only have 2 if statements,
# instead of 6 if statements. if option == 5 or 6 we need to make the value
# a str to print them
def changeGameOption(option, name):
    game = collection.find_one({"_id": name})
    if option == 2:
        return "genre 1", "genre1", game["genre1"]
    elif option == 3:
        return "genre 2", "genre2", game["genre2"]
    elif option == 4:
        return "developer", "developer", game["developer"]
    elif option == 5:
        return "release year", "year", str(game["year"])
    elif option == 6:
        return "rating", "rating", str(game["rating"])


# helper function used to make code more readable
# changes an attribute of a game
def changeGameHelp(name):
    print("What would you like to change about " + name)
    print("[1]Name")
    print("[2]Genre 1")
    print("[3]Genre 2")
    print("[4]Developer")
    print("[5]Year")
    print("[6]Rating")
    print("[0]Nothing")
    option = choice()
    while option != 0:
        # _id == name of game, _id is the primary key in mongoDB
        # _id cant be changed like any other field, to change the _id
        # we need to make a copy of the game. Then change the _id of the copy
        # insert the copy into the database and then delete 
        # the orignal version of the game
        if option == 1:
            print("Original name:" + name)
            newName = input("What would you like to change the name to?\n")
            cursor = collection.find_one({"_id": name})
            cursor["_id"] = newName
            collection.insert_one(cursor)
            collection.delete_one({"_id": name})
            collection.update_one({"_id": name},
                                  {"$set": {"name_lower": newName.lower()}})
            printGame(cursor)
        elif 1 < option <= 6:
            # used to change every attribute but the _id of a game
            attribute, key, value = changeGameOption(option, name)
            print("Original " + attribute + ":" + value)
            newValue = input("New:")
            collection.update_one({"_id": name}, {"$set": {key: newValue}})
            printGame(collection.find_one({"_id": name}))
            break
        else:
            print("Thats not a valid option")
        option = choice()
    return


# used to change an attribute of a game
def changeGame():
    i = 0
    gameName = input("Which game would you like to change?\n")
    answer = collection.find_one({"name_lower": gameName.lower()})
    if answer is None:
        # checks whether there are games in the database that have
        # gameName as a substring
        answer = collection.find({"name_lower": {"$regex": gameName.lower()}})
        result = list(answer)
        # if there are games in the database that match gameName,
        # print them out
        if len(result) != 0:
            print("Did you mean?")
            searchHelpChange(result, "change")
        else:
            print("No game matches that name!")
    # if gameName matches directly
    else:
        printGame(answer)
        changeMenu()
        option = choice()
        while option != 1:
            if option == 2:
                break
            else:
                print("Thats not a valid option")
            option = choice()
        changeGameHelp(answer["_id"])

    return


# used to delete a game from the database
def deleteGame():
    gameName = input("Name van game?\n")
    collection.delete_one({"name_lower": gameName.lower()})


# gets input from user. Limits inputs to digits
def choice():
    option = input("Enter your option: ")
    while not option.isdigit():
        print("Thats not a valid option")
        option = input("Enter your option: ")
    return int(option)


# make connection to database
# myclient = pymongo.MongoClient("mongodb://admin:blabla208@192.168.138.74")
myclient = pymongo.MongoClient("mongodb+srv://user51:user51@indieman"
                               ".bkil2.mongodb.net/indieman")
mydb = myclient["INDIEPACMAN"]
collection = mydb["games2"]

# menu
menu()
option = choice()
while option != 0:
    if option == 1:
        searchName()
    elif option == 2:
        addGame()
    elif option == 3:
        deleteGame()
    elif option == 4:
        changeGame()
    else:
        print("Thats not a valid option")

    print()
    menu()
    option = choice()

print("Thanks for using our service. Goodbye")
