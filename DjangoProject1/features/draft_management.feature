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