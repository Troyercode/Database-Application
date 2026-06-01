"""
README: To use this script simply run it and follow the menu options as they are presented in the terminal. 
"""
import pyodbc
import time
import random

MENU = "---------\nMain Menu\n---------\n1. Search Business\n2. Search Users\n3. Exit"\
       "\n\nEnter a number to choose an option: "
ID_STRING = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxqz0123456789-_"
SEARCH_BUSINESS_ORDER = "1. Numerically by number of stars\n2. Alphabetically by city\n"\
"3. Alphabetically by name\n4. Unordered\n"

def login(cur):
    i = 0
    attempts = 3        
    matching_uid = []
    user_id = ''
    exit = False
    while(len(matching_uid) <= 0 and i < attempts):
        if (not i == 0):
            time.sleep(0.25)
            print(f"user ID is invalid, attempts left: {attempts-i}")
        user_id = input("Enter your user ID: ")
        matching_uid = cur.execute("SELECT* FROM user_yelp WHERE ? = user_id", (user_id,)).fetchall()
        i += 1
    if(len(matching_uid) <= 0 and i >= attempts):
        exit = True 
        print("Number of attempts exceeded, exiting...")
    elif (len(matching_uid) > 1):
        exit = True  
        print("Error: more than one matching user ID, exiting...")
    if exit == False:
        time.sleep(0.25)
        print("login successful\n")
    return (exit, user_id)

def SearchBusiness(cur, connection, UID):
    query_result = []
    main_menu, done_filtering = False, False
    filtersONOFF = [False, False, False]
    filters = ["1. Select minimum number of stars", "2. Search by city", "3. Search by name"]
    SEARCH_MENU = "4. Reset filters\n5. Execute filters\n6. Back to main menu\n"
    select_min_stars, select_city, select_name = '1', '2', '3'
    select_reset, select_execute, select_exit = '4', '5', '6'
    order_stars, order_city, order_name, order_none = '1', '2', '3', '4'
    query = "SELECT business_id, name, address, city, stars, review_count FROM business"
    min_stars_in, city_in, name_in = '', '', ''
    while(not main_menu):
        while(not done_filtering and not main_menu):
            #present menu options, and prepare different queries depending on user responses
            time.sleep(0.25)
            print("\n-----------------\nSearch Businesses\n-----------------")
            for i in range(3):
                if filtersONOFF[i]:
                    print(filters[i] + " (filter added)")
                else:
                    print(filters[i])
            print(SEARCH_MENU)
            choice = input("Enter a number to filter or manage your search: ")
            time.sleep(0.25)
            if choice == select_min_stars:
                if not filtersONOFF[0]:
                    min_stars_in = input("Enter the minimum number of stars: ")
                    try:
                        min_stars_in = float(min_stars_in)
                    except BaseException:
                        print("\nInput could not be interpreted as number, try again")
                    else:
                        min_stars_in = round(min_stars_in, 1)
                        if True in filtersONOFF:
                            query = query + " AND stars >= " + f"{min_stars_in}"
                        else:
                            query = query +  " WHERE " + "stars >= " + f"{min_stars_in}"
                        filtersONOFF[0] = True
                else:
                    print("Filter already added!")
            elif choice == select_city:
                if not filtersONOFF[1]:
                    city_in = input("Select a city: ")
                    if True in filtersONOFF:
                        query = query + " AND city LIKE " + f"'{city_in}'"
                    else:
                        query = query + " WHERE " + "city LIKE " + f"'{city_in}'"
                    filtersONOFF[1] = True
                else:
                    print("Filter already added!")
            elif choice == select_name:
                if not filtersONOFF[2]:
                    name_in = input("Enter the name of a business: ")
                    if True in filtersONOFF:
                        query = query + " AND name LIKE " + f"'%{name_in}%'"
                    else:
                        query = query + " WHERE " + "name LIKE " + f"'%{name_in}%'"
                    filtersONOFF[2] = True
                else:
                    print("Filter already added!")
            elif choice == select_reset:
                query = "SELECT business_id, name, address, city, stars, review_count FROM business"
                for i in range(3):
                    filtersONOFF[i] = False
            elif choice == select_execute:
                try:
                    query += ";"
                    query_result = cur.execute(query).fetchall()
                except pyodbc.Error:
                    print(f"An error occured while processing the search.")
                    print("Please try again. Resetting search.")
                    query = "SELECT business_id, name, address, city, stars, review_count FROM business"
                    for i in range(3):
                       filtersONOFF[i] = False
                    done_filtering = False
                else:
                    done_filtering = True
            elif choice == select_exit:
                done_filtering = True
                main_menu = True
            else:
                print("Invalid menu option, try again")

        if(main_menu):
            #'return to main menu' was chosen
            break
        if(len(query_result) == 0):
            #no results found
            time.sleep(0.25)
            print("\nNo results found.")
        else:
            #results found, choose sorting order
            print("\n-------------\nOrder Search\n-------------")
            print(SEARCH_BUSINESS_ORDER)
            order_choice = input("Enter a number to choose how to display your search: ")
            if order_choice == order_stars:
                query_result.sort( key=lambda row: float(row.stars))
            elif order_choice == order_city:
                query_result.sort(key=lambda row: row.city.lower())
            elif order_choice == order_name:
                query_result.sort( key=lambda row: row.name.lower())
            elif order_choice == order_none:
                print()
            else:
                print("Invalid menu option, displaying unordered results:")
            
            #print the formatted output
            for row in query_result:
                for i in range(len(row)):
                    if row[i] == None:
                        row[i] = "NULL"
            truncated = False
            max_name_overflow, max_address_overflow, max_city_overflow = 35, 35, 26
            max_name = min(max((len(max(query_result, key=lambda row: len(row.name)).name) + 1), 5), max_name_overflow)
            max_address = min(max((len(max(query_result, key=lambda row: len(row.address)).address) + 1), 8), max_address_overflow)
            max_city = min(max((len(max(query_result, key=lambda row: len(row.city)).city) + 1), 5), max_city_overflow)
            header = "id"+' '*21+"name"+' '*(max_name-4)+"address"+' '*(max_address-7)+"city"+' '*(max_city-4)+"stars"
            print(len(header)*'-' + '\n' +header + '\n' +len(header)*'-')
            for row in query_result:
                print(f"{row[0]:<23}", end='')
                if(max_name <= len(str(row[1]))):
                    truncated = True
                    print(f"{row[1]:<{max_name-4}.{max_name-4}}... ", end='')
                else:
                    print(f"{row[1]:<{max_name}.{max_name}}", end='')
                if (max_address <= len(row[2])):
                    truncated = True
                    print(f"{row[2]:<{max_address-4}.{max_address-4}}... ", end='')
                else:
                    print(f"{row[2]:<{max_address}.{max_address}}", end='')
                if(max_city <= len(row[3])):
                    truncated = True
                    print(f"{row[3]:<{max_city-4}.{max_city-4}}... ", end='')
                else:
                    print(f"{row[3]:<{max_city}.{max_city}}", end='')
                print(f"{row[4]:<6}")
            if truncated:
                print("\nSome reselts were truncated to fit to the terminal.")
            ReviewBusiness(cur, connection, query_result, UID)
        #reset search
        for i in range(3):
            filtersONOFF[i] = False
        done_filtering = False
        query = "SELECT business_id, name, address, city, stars, review_count FROM business"

def SearchUser(cur, connection, UID):
    query_result = []
    main_menu, done_filtering = False, False
    filtersONOFF = [False, False, False]
    filters = ["1. Search for user name", \
               "2. Filter by minimum number of reviews", \
                "3. Filter by minimum average stars"]
    SEARCH_MENU = "4. Reset filters\n5. Execute filters\n6. Back to main menu\n"
    select_name, select_r_count, select_a_stars = '1', '2', '3'
    select_reset, select_execute, select_exit = '4', '5', '6'
    name_in, r_count_in, avg_stars_in = '', '', ''
    query = "SELECT user_id, name, review_count, useful, "\
        "funny, cool, average_stars, yelping_since FROM user_yelp"
    while(not main_menu):
        while(not done_filtering and not main_menu):
            #present menu options, and prepare different queries depending on user responses
            time.sleep(0.25)
            print("\n-----------------\nSearch Businesses\n-----------------")
            for i in range(3):
                if filtersONOFF[i]:
                    print(filters[i] + " (filter added)")
                else:
                    print(filters[i])
            print(SEARCH_MENU)
            choice = input("Enter a number to filter or manage your search: ")
            time.sleep(0.25)
            if choice == select_name:
                if not filtersONOFF[0]:
                    name_in = input("Enter a user name: ")
                    if True in filtersONOFF:
                        query = query + " AND name LIKE " + f"'%{name_in}%'"
                    else:
                        query = query + " WHERE " + "name LIKE " + f"'%{name_in}%'"
                    filtersONOFF[0] = True
                else:
                    print("Filter already added!")
            elif choice == select_r_count:
                if not filtersONOFF[1]:
                    r_count_in = input("Select the minimum review count: ")
                    try:
                        r_count_in = float(r_count_in)
                    except BaseException:
                        print("\nInput could not be interpreted as number, try again")
                    else:
                        if True in filtersONOFF:
                            query = query + " AND review_count >= " + f"{r_count_in}"
                        else:
                            query = query +  " WHERE " + "review_count >= " + f"{r_count_in}"
                        filtersONOFF[1] = True
                else:
                    print("Filter already added!")
            elif choice == select_a_stars:
                if not filtersONOFF[2]:
                    avg_stars_in = input("Enter the minimum average number of stars: ")
                    try:
                        avg_stars_in = float(avg_stars_in)
                    except BaseException:
                        print("\nInput could not be interpreted as number, try again")
                    else:
                        avg_stars_in = round(avg_stars_in, 2)
                        if True in filtersONOFF:
                            query = query + " AND average_stars >= " + f"{avg_stars_in}"
                        else:
                            query = query +  " WHERE " + "average_stars >= " + f"{avg_stars_in}"
                        filtersONOFF[2] = True
                else:
                    print("Filter already added!")
            elif choice == select_reset:
                query = "SELECT user_id, name, review_count, useful, "\
                        "funny, cool, average_stars, yelping_since FROM user_yelp"
                for i in range(3):
                    filtersONOFF[i] = False
            elif choice == select_execute:
                try:
                    query += ";"
                    query_result = cur.execute(query).fetchall()
                except pyodbc.Error:
                    print(f"An error occured while processing the search.")
                    print("Please try again. Resetting search.")
                    query = "SELECT user_id, name, review_count, useful, "\
                            "funny, cool, average_stars, yelping_since FROM user_yelp"
                    for i in range(3):
                       filtersONOFF[i] = False
                    done_filtering = False
                else:
                    done_filtering = True
            elif choice == select_exit:
                done_filtering = True
                main_menu = True
            else:
                print("Invalid menu option, try again")
        if(main_menu):
            #'return to main menu' was chosen
            break
        if(len(query_result) == 0):
            #no results in the query
            time.sleep(0.25)
            print("\nNo results found.")
        else:
            #results found, sort, then print results
            query_result.sort( key=lambda row : row.name.lower())
            for row in query_result:
                for i in range(len(row)):
                    if row[i] == None:
                        row[i] = "NULL"
            id_len, name_len, rev_len, use_len = 2, 4, 9, 6
            fun_len, cool_len, since_len = 5, 4, 13
            max_id, max_since, max_avg = 23, 20, 10
            longest_str = len(max(query_result, key=lambda row: len(row.name)).name) + 1
            max_name = max(longest_str, name_len + 1)
            longest_str = len(str(max(query_result, key=lambda row: len(str(row.review_count))).review_count)) + 1
            max_review = max(longest_str, rev_len + 1)
            longest_str = (len(str(max(query_result, key=lambda row: len(str(row.useful))).useful)) + 1)
            max_useful = max(longest_str, use_len + 1)
            longest_str = len(str(max(query_result, key=lambda row: len(str(row.funny))).funny)) + 1
            max_funny = max(longest_str, fun_len + 1)
            longest_str = len(str(max(query_result, key=lambda row: len(str(row.cool))).cool)) + 1
            max_cool = max(longest_str, cool_len +1)
            header = "id"+' '*(max_id-id_len)+"name"+' '*(max_name-name_len)+"rev_count"+' '*(max_review-rev_len) +\
            "useful"+' '*(max_useful-use_len)+"funny"+' '*(max_funny-fun_len)+"cool"+' '*(max_cool-cool_len) +\
            "avg_stars "+ "yelping_since" +' '*(max_since-since_len)
            print(len(header)*'-' + '\n' +header + '\n' +len(header)*'-')
            for row in query_result:
                print(f"{row[0]:<{max_id}}", end='')
                print(f"{row[1]:<{max_name}}", end='')
                print(f"{row[2]:<{max_review}}", end='')
                print(f"{row[3]:<{max_useful}}", end='')
                print(f"{row[4]:<{max_funny}}", end='')
                print(f"{row[5]:<{max_cool}}", end='')
                print(f"{row[6]:<{max_avg}}", end='')
                print(f"{str(row[7]):<{max_since}}")
            MakeFriend(cur, connection, query_result, UID)
        #reset search       
        for i in range(3):
            filtersONOFF[i] = False
        done_filtering = False
        query = "SELECT user_id, name, review_count, useful, "\
                "funny, cool, average_stars, yelping_since FROM user_yelp"

def MakeFriend(cur, connection, user_tuples, UID):
    select_add = input("\nWould you like to add a user from the search result as a friend? (Y/N) ")
    done_adding = False
    found = 0
    query = ''
    while(not done_adding):
        query = "INSERT INTO friendship VALUES ('" + UID
        if(select_add.lower() == 'y'):
            #add friend
            select_uid = input("Enter the user id of the friend you would like to make: ")
            #check that the id is valid
            for row in user_tuples:
                if(select_uid in row):
                    found += 1
            if(found == 0):
                print("Selected user not found in search results")
            else:
                #if the id is valid, prepare and try the query
                query = query + "', '"+select_uid+"');"
                try:
                    cur.execute(query)
                except pyodbc.Error:
                    print(f"An error occured while executing the query. Friend not added.")
                else:
                    try:
                        connection.commit()
                    except pyodbc.Error:
                        print(f"An error occured while committing the query. Friend not added.")
                        connection.rollback()
                    else:
                        time.sleep(0.25)
                        print("Friend successfully added")
        else:
            #stop adding friends
            if(select_add.lower() != 'n'):
                print("input could not be understood as a valid choice")
            print("Returning to user search menu...")
            break
        time.sleep(0.25)
        select_cont = input("Continue adding friends? (Y/N) ")
        if(select_cont.lower() != 'y'):
            done_adding = True
            if(select_cont.lower() != 'n'):
                print("input could not be understood as a valid choice")
            print("Returning to user search menu...")
    return

def generate_review_id():
    id_len = 22
    possible_chars_len = len(ID_STRING)
    id = ''
    for i in range(id_len):
        id += ID_STRING[random.randint(0, possible_chars_len - 1)]
    return id

def generate_unique_id(cur):
    #this is a helper function that finds a new review id that doesn't already exist in the database
    query = 'SELECT * FROM review WHERE review_id = ?'
    id = ''
    result = ['']
    while(len(result) > 0):
        id = generate_review_id()
        result = cur.execute(query, (id, )).fetchall()
    return id

def ReviewBusiness(cur, connection, business_tuples, UID):
    """
    Note: There are discrepencies between the number of reveiws in the 'reviews' table and the numbers
    noted per business in the 'business' table (the average stars in 'business' also doesn't align with 'reveiws'). 
    My solution to this is to use the review count from 'business' to generate the updated review count (to match the tests), 
    but used the average number of stars found by calculating the average from the 'reveiws' table
    because otherwise it would not be possible to calculate an accurate average from 'business'.
    """
    select_add = input("\nWould you like to add a review for a business from your search results? (Y/N) ")
    done_adding = False
    stars_in = 0
    new_review_num = 0
    new_avg = 0
    review_id = ''
    found = 0
    insert_query = ''
    avg_stars_query = ''
    update_business_query = ''
    bid_row = ''
    
    while(not done_adding):
        insert_query = "INSERT INTO review (review_id, user_id, business_id, stars) VALUES"
        avg_stars_query = "SELECT SUM(stars), COUNT(stars) "\
                        "FROM review GROUP BY business_id HAVING business_id = "
        update_business_query = "UPDATE business SET"
        if(select_add.lower() == 'y'):
            select_bid = input("Enter the business id of the business you would like to review: ")
            #check that the business id is valid
            for row in business_tuples:
                if(select_bid in row):
                    bid_row = row
                    found += 1
                    break
            if(found == 0):
                print("Selected business not found in search results")
            else:
                #if the business id is valid, then ask for the number of stars and prepare the update queries
                review_id = generate_unique_id(cur)
                stars_in = input("Enter the number of stars (between 1 and 5): ")
                try:
                    stars_in = int(stars_in)
                except:
                    print("\nInput could not be interpreted as a whole number, try again")
                else:
                    try:
                        insert_query += " ('" + review_id + "', " + "'" + UID + "', " + "'" + select_bid + "', " + str(stars_in) + " );"
                        avg_stars_query += "'" + select_bid + "';"
                        sum_and_count = cur.execute(avg_stars_query).fetchall()
                        if not len(sum_and_count) == 0:
                            new_review_num = bid_row[5] + 1
                            new_avg = round((sum_and_count[0][0] + stars_in)/(sum_and_count[0][1] + 1), 1)
                        else:
                            new_review_num = bid_row[5] + 1
                            new_avg = stars_in

                        update_business_query += " stars = " + str(new_avg) + ", review_count = " + \
                                                 str(new_review_num) + " " + "WHERE business_id = " + "'" + select_bid + "';"
                        cur.execute(insert_query)
                        cur.execute(update_business_query)
                    
                    except pyodbc.Error:
                        print(f"An error occured while executing the query. Review not added.")
                    else:
                        try:
                            connection.commit()
                        except pyodbc.Error:
                            print(f"An error occured while committing the query. Review not added.")
                            connection.rollback()
                        else:
                            time.sleep(0.25)
                            print("Review successfully added.")
        else:
            if(select_add.lower() != 'n'):
                print("input could not be understood as a valid choice")
            print("Returning to business search menu...")
            break
        time.sleep(0.25)
        select_cont = input("Add another review? (Y/N) ")
        if(select_cont.lower() != 'y'):
            done_adding = True
            if(select_cont.lower() != 'n'):
                print("input could not be understood as a valid choice")
            print("Returning to business search menu...")
    return

def main():
    c_str = "Driver={ODBC Driver 17 for SQL Server};"\
    "Server=CS-DB-MS1;"\
    "Database=mtroyer354;"\
    "Trusted_Connection=yes;"
    search_business, search_users, select_exit = '1', '2', '3'
    connection = pyodbc.connect(c_str)
    cur = connection.cursor()
    exit_uid_tuple = login(cur)
    exit = exit_uid_tuple[0]
    while(not exit):
        choice = input(MENU)
        time.sleep(0.5)
        if(choice == search_business):
            SearchBusiness(cur, connection, exit_uid_tuple[1])
        elif(choice == search_users):
            SearchUser(cur, connection, exit_uid_tuple[1])
        elif(choice == select_exit):
            exit = True
            print("You have successfully logged out\nexiting")
        else:
            print("Invalid menu option, try again\n")

    cur.close()
    connection.close()

main()

# WEwjYKHh84PryzVRpwaUlw
# oIvc0PM_vYtyJk9CcluawQ
# D__iHPVDEhqQr0ZkGt___Q
# Hh4z0AC87A31KTN8czg2nw
# PJ43IZYt0UrknN_P4UJfFQ
