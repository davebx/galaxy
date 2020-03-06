from .framework import (
    selenium_test,
    SeleniumTestCase
)


class HistoryMultiViewTestCase(SeleniumTestCase):

    ensure_registered = True

    @selenium_test
    def test_switch_history(self):
        '''
        1. Load the multi history view. There should be a selector for the button
           to create a new history.
        2. Create a new history. This *should* automatically switch to the newly
           created history.
        3. Switch back to the original history. A button should appear on the old,
           previously created history that allows switching back to that one, and
           the history ID should now match the ID of the history with which we
           started.
        '''
        self.home()
        original_history_id = self.current_history_id()
        # Load the multi-view
        self.components.history_panel.multi_view_button.wait_for_and_click()
        # Creating a new history should automatically switch to it
        self.components.multi_history_view.create_new_button.wait_for_and_click()
        new_history_id = self.current_history_id()
        # Otherwise this assertion would fail
        self.screenshot("multi_history_switch_created_history")
        self.assertNotEqual(original_history_id, new_history_id)
        # Switch back to the original history
        switch_button = self.components.multiple_histories._(history_id=original_history_id).switch_button
        # self.wait_for_visible(switch_button)
        switch_button.wait_for_and_click()
        new_switch_button = self.components.multiple_histories._(history_id=new_history_id).switch_button
        self.wait_for_visible(new_switch_button)
        self.screenshot("multi_history_switch_changed_history")
        self.assertEqual(original_history_id, self.current_history_id())

    @selenium_test
    def test_create_new_old_slides_next(self):
        history_id = self.current_history_id()
        input_collection = self.dataset_collection_populator.create_list_in_history(history_id, contents=["0", "1", "0", "1"]).json()
        input_hid = input_collection["hid"]

        self.home()

        hdca_selector = self.history_panel_wait_for_hid_state(input_hid, "ok")

        self.components.history_panel.multi_view_button.wait_for_and_click()
        self.components.multi_history_view.create_new_button.wait_for_and_click()
        self.components.multi_history_view.drag_drop_help.wait_for_visible()
        self.wait_for_visible(hdca_selector)
        self.screenshot("multi_history_collection")

    @selenium_test
    def test_list_list_display(self):
        history_id = self.current_history_id()
        collection = self.dataset_collection_populator.create_list_of_list_in_history(history_id).json()
        collection_hid = collection["hid"]

        self.home()

        self.components.history_panel.multi_view_button.wait_for_and_click()

        selector = self.history_panel_wait_for_hid_state(collection_hid, "ok")
        self.click(selector)
        first_level_element_selector = selector.descendant(".dataset-collection-element")
        self.wait_for_and_click(first_level_element_selector)
        dataset_selector = first_level_element_selector.descendant(".dataset")
        self.wait_for_and_click(dataset_selector)

        self.sleep_for(self.wait_types.UX_TRANSITION)
        self.screenshot("multi_history_list_list")

    @selenium_test
    def test_list_list_list_display(self):
        history_id = self.current_history_id()
        collection = self.dataset_collection_populator.create_nested_collection(history_id, collection_type="list:list:list").json()
        collection_hid = collection["hid"]

        self.home()

        self.components.history_panel.multi_view_button.wait_for_and_click()

        selector = self.history_panel_wait_for_hid_state(collection_hid, "ok")
        self.click(selector)
        first_level_element_selector = selector.descendant(".dataset-collection-element")
        self.wait_for_and_click(first_level_element_selector)
        second_level_element_selector = first_level_element_selector.descendant(".dataset-collection-element")
        self.wait_for_and_click(second_level_element_selector)
        dataset_selector = first_level_element_selector.descendant(".dataset")
        self.wait_for_and_click(dataset_selector)

        self.sleep_for(self.wait_types.UX_TRANSITION)
        self.screenshot("multi_history_list_list_list")
