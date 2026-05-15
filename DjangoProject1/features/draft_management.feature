Feature: Futdraft management

  As a registered user
  I want to manage my own Futdrafts
  So that I can create and view my teams without using Django admin

  Scenario: Anonymous user cannot access my drafts
    When I go to my drafts page without logging in
    Then I should be redirected to the login page

  Scenario: Registered user can create a draft
    Given there is a registered user
    And there are players and a lineup in the database
    When I log in
    And I create a draft named "My first draft"
    Then I should see the draft "My first draft" in my drafts page

  Scenario: Registered user can edit own draft
    Given there is a registered user
    And there are players and a lineup in the database
    And the user has a draft named "Old draft"
    When I log in
    And I edit the draft "Old draft" to "Updated draft"
    Then I should see the draft "Updated draft" in my drafts page
    And I should not see the draft "Old draft" in my drafts page

  Scenario: Registered user can delete own draft
    Given there is a registered user
    And there are players and a lineup in the database
    And the user has a draft named "Draft to delete"
    When I log in
    And I delete the draft "Draft to delete"
    Then I should not see the draft "Draft to delete" in my drafts page

  Scenario: User cannot edit another user's draft
    Given there are two registered users
    And there are players and a lineup in the database
    And the second user has a draft named "Private draft"
    When I log in
    And I try to edit the other user's draft
    Then the request should fail with a security error

  Scenario: User cannot delete another user's draft
    Given there are two registered users
    And there are players and a lineup in the database
    And the second user has a draft named "Private draft to delete"
    When I log in
    And I try to delete the other user's draft
    Then the request should fail with a security error

  Scenario: User cannot create a draft with empty name
    Given there is a registered user
    And there are players and a lineup in the database
    When I log in
    And I try to create a draft with an empty name
    Then the draft creation should fail with the error "El nom del draft no pot estar buit."