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

    Scenario: Search recommendations by source_item_id and filtered by status
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "123" in the results
        When I press the "Clear" button
        And I set the "src item id" to "123"
        And I select "Valid" in the "Status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "VALID" in the results
        And I should not see "DEPRECATED" in the results
        And I should not see "OUT_OF_STOCK" in the results
        And I should not see "UNKNOWN" in the results
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "123" in the "src item id" field
        And I should see "456" in the "tgt item id" field
        And I should see "Valid" in the "Status" dropdown

    Scenario: Retrieve recommendations by source_item_id
        When I visit the "Home Page"
        And I select "Valid" in the "Status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "123" in the results
        When I press the "Clear" button
        And I set the "src item id" to "123"
        And I select "Valid" in the "Status" dropdown
        And I press the "retrieve-by-src-item-id" button
        Then I should see the message "Success"
        And I should see "123" in the "src item id" field
        And I should see "456" in the "tgt item id" field
        And I should see "0.5" in the "Weight" field
        And I should see "10" in the "num of likes" field
        And I should see "Valid" in the "Status" dropdown
    
    Scenario: Retrieve recommendations by source_item_id that does not exist
        When I visit the "Home Page"
        And I select "Valid" in the "Status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        When I press the "Clear" button
        And I set the "src item id" to "1"
        And I press the "retrieve-by-src-item-id" button
        Then I should see the message "No recommendations found!"

    Scenario: Delete a recommendation
        When I visit the "Home Page"
        And I select "Up Sell" in the "Type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Delete" button
        Then I should see the message "Recommendation has been deleted!"
        When I copy the "Id" field
        And I press the "Clear" button
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "404 Not Found"

    Scenario: Update a Recommendation
        When I visit the "Home Page"
        And I set the "src item id" to "123"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "456" in the "tgt item id" field
        And I should see "UP_SELL" in the "type" field
        And I should see "0.5" in the "weight" field
        And I should see "VALID" in the "status" field
        And I should see "10" in the "num of likes" field
        When I change "src item id" to "996"
        When I change "tgt item id" to "879"
        And I press the "Update" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "996" in the "src item id" field
        And I should see "879" in the "tgt item id" field
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "996" in the results
        And I should see "879" in the results
        And I should not see "123" in the results

    Scenario: Create a Recommendation
        When I visit the "Home Page"
        And I set the "src item id" to "888"
        And I set the "tgt item id" to "999"
        And I select "Up Sell" in the "Type" dropdown
        And I select "Unknown" in the "Status" dropdown
        And I set the "weight" to "0.7"
        And I set the "num of likes" to "9"
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "Id" field should be empty
        And the "src item id" field should be empty
        And the "tgt item id" field should be empty
        And the "weight" field should be empty
        And the "num of likes" field should be empty
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "888" in the "src item id" field
        And I should see "999" in the "tgt item id" field
        And I should see "Up Sell" in the "Type" dropdown
        And I should see "Unknown" in the "Status" dropdown
        And I should see "0.7" in the "weight" field
        And I should see "9" in the "num of likes" field
