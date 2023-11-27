Feature: The recommendation service back-end
    As a Product Manager
    I need a RESTful catalog service
    So that I can keep track of all recommendations

    Background:
        Given the following recommendations

            | id | source_item_id | target_item_id | type       | weight | status       | number_of_likes |
            | 1  | 123            | 456            | UP_SELL    | 0.5    | VALID        | 10              |
            | 2  | 789            | 101            | CROSS_SELL | 0.8    | OUT_OF_STOCK | 5               |
            | 3  | 222            | 333            | ACCESSORY  | 0.2    | DEPRECATED   | 2               |


    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Recommendation Demo RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Read recommendations by type
        When I visit the "Home Page"
        And I select "Up Sell" in the "Type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "UP_SELL" in the results
        And I should not see "CROSS_SELL" in the results
        And I should not see "ACCESSORY" in the results
        And I should not see "COMPLEMENTARY" in the results
        And I should not see "SUBSTITUTE" in the results
        When I press the "Clear" button
        And I select "Cross Sell" in the "Type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "CROSS_SELL" in the results
        And I should not see "UP_SELL" in the results
        And I should not see "ACCESSORY" in the results
        And I should not see "COMPLEMENTARY" in the results
        And I should not see "SUBSTITUTE" in the results
        When I press the "Clear" button
        And I select "Accessory" in the "Type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "ACCESSORY" in the results
        And I should not see "UP_SELL" in the results
        And I should not see "CROSS_SELL" in the results
        And I should not see "COMPLEMENTARY" in the results
        And I should not see "SUBSTITUTE" in the results

    Scenario: Read recommendations by status
        When I visit the "Home Page"
        And I select "Valid" in the "Status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "VALID" in the results
        And I should not see "UNKNOWN" in the results
        And I should not see "OUT_OF_STOCK" in the results
        And I should not see "DEPRECATED" in the results
        When I press the "Clear" button
        And I select "Deprecated" in the "Status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "DEPRECATED" in the results
        And I should not see "VALID" in the results
        And I should not see "OUT_OF_STOCK" in the results
        And I should not see "UNKNOWN" in the results
        When I press the "Clear" button
        And I select "Out of Stock" in the "Status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "OUT_OF_STOCK" in the results
        And I should not see "VALID" in the results
        And I should not see "UNKNOWN" in the results
        And I should not see "DEPRECATED" in the results

    Scenario: Retrive recommendations by id
        When I visit the "Home Page"
        And I select "Up Sell" in the "Type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "123" in the "src item id" field
        And I should see "456" in the "tgt item id" field
        And I should see "0.5" in the "Weight" field
        And I should see "10" in the "num of likes" field

    Scenario: List all recommendations
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "123" in the results
        And I should see "789" in the results
        And I should see "222" in the results
        And I should see "456" in the results
        And I should see "101" in the results
        And I should see "333" in the results
        And I should see "UP_SELL" in the results
        And I should see "CROSS_SELL" in the results
        And I should see "ACCESSORY" in the results
        And I should not see "362" in the results
        And I should not see "753" in the results
        
    Scenario: Retrive recommendations by source_item_id and filtered by status
        When I visit the "Home Page"
        And I type in "123" in search field "source_item_id"
        And I select "VALID" in the "status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "123" in the "src item id" field
        And I should see "456" in the "tgt item id" field
        And I should see "0.5" in the "Weight" field
        And I should see "10" in the "num of likes" field

# Scenario: Create a Pet
#     When I visit the "Home Page"
#     And I set the "Name" to "Happy"
#     And I set the "Category" to "Hippo"
#     And I select "False" in the "Available" dropdown
#     And I select "Male" in the "Gender" dropdown
#     And I set the "Birthday" to "06-16-2022"
#     And I press the "Create" button
#     Then I should see the message "Success"
#     When I copy the "Id" field
#     And I press the "Clear" button
#     Then the "Id" field should be empty
#     And the "Name" field should be empty
#     And the "Category" field should be empty
#     When I paste the "Id" field
#     And I press the "Retrieve" button
#     Then I should see the message "Success"
#     And I should see "Happy" in the "Name" field
#     And I should see "Hippo" in the "Category" field
#     And I should see "False" in the "Available" dropdown
#     And I should see "Male" in the "Gender" dropdown
#     And I should see "2022-06-16" in the "Birthday" field

# Scenario: List all pets
#     When I visit the "Home Page"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: Search for dogs
#     When I visit the "Home Page"
#     And I set the "Category" to "dog"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should not see "kitty" in the results
#     And I should not see "leo" in the results

# Scenario: Search for available
#     When I visit the "Home Page"
#     And I select "True" in the "Available" dropdown
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the results
#     And I should see "kitty" in the results
#     And I should see "sammy" in the results
#     And I should not see "leo" in the results

# Scenario: Update a Pet
#     When I visit the "Home Page"
#     And I set the "Name" to "fido"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "fido" in the "Name" field
#     And I should see "dog" in the "Category" field
#     When I change "Name" to "Loki"
#     And I press the "Update" button
#     Then I should see the message "Success"
#     When I copy the "Id" field
#     And I press the "Clear" button
#     And I paste the "Id" field
#     And I press the "Retrieve" button
#     Then I should see the message "Success"
#     And I should see "Loki" in the "Name" field
#     When I press the "Clear" button
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "Loki" in the results
#     And I should not see "fido" in the results

# Scenario: Delete a Pet
#     When I visit the "Home Page"
#     And I set the "Name" to "sammy"
#     And I press the "Search" button
#     Then I should see the message "Success"
#     And I should see "sammy" in the "Name" field
#     And I should see "snake" in the "Category" field
#     When I press the "Delete" button
#     Then I should see the message "Pet has been Deleted!"