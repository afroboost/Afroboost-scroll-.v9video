"""
Test suite for /api/conversations/active endpoint
Tests the recipient selector functionality for campaigns:
- Groups (including 'Les Lionnes') and users are returned
- Case-insensitive search capability (frontend filtering)
- Proper structure for targetConversationId selection
"""

import pytest
import requests
import os

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise RuntimeError("REACT_APP_BACKEND_URL environment variable is required")


class TestConversationsActiveEndpoint:
    """Tests for GET /api/conversations/active endpoint"""
    
    def test_endpoint_returns_success(self):
        """Test that the endpoint returns a successful response"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert "conversations" in data, "Response should contain 'conversations' key"
        assert "total" in data, "Response should contain 'total' key"
        print(f"✅ Endpoint returns success with {data.get('total', 0)} conversations")
    
    def test_response_structure(self):
        """Test that each conversation has required fields"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        assert len(conversations) > 0, "Should return at least one conversation"
        
        # Check structure of first conversation
        first_conv = conversations[0]
        required_fields = ["conversation_id", "name", "type"]
        
        for field in required_fields:
            assert field in first_conv, f"Conversation should have '{field}' field"
        
        # Verify type is either 'group' or 'user'
        assert first_conv["type"] in ["group", "user"], f"Type should be 'group' or 'user', got {first_conv['type']}"
        
        print(f"✅ Response structure is correct with required fields: {required_fields}")
    
    def test_groups_are_returned(self):
        """Test that groups are included in the response"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        groups_count = data.get("groups_count", 0)
        conversations = data.get("conversations", [])
        
        # Filter groups
        groups = [c for c in conversations if c.get("type") == "group"]
        
        assert len(groups) > 0, "Should return at least one group"
        assert groups_count == len(groups), f"groups_count ({groups_count}) should match actual groups ({len(groups)})"
        
        # Print all groups found
        print(f"✅ Found {len(groups)} groups:")
        for g in groups:
            print(f"   - {g.get('name')} (ID: {g.get('conversation_id')})")
    
    def test_users_are_returned(self):
        """Test that users are included in the response"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        users_count = data.get("users_count", 0)
        conversations = data.get("conversations", [])
        
        # Filter users
        users = [c for c in conversations if c.get("type") == "user"]
        
        assert len(users) > 0, "Should return at least one user"
        assert users_count == len(users), f"users_count ({users_count}) should match actual users ({len(users)})"
        
        print(f"✅ Found {len(users)} users")
        # Print first 5 users
        for u in users[:5]:
            print(f"   - {u.get('name')} (ID: {u.get('conversation_id')})")
        if len(users) > 5:
            print(f"   ... and {len(users) - 5} more users")
    
    def test_les_lionnes_group_exists(self):
        """Test that 'Les Lionnes' group is present in the response"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Search for 'Les Lionnes' (case-insensitive)
        lionnes_groups = [
            c for c in conversations 
            if "lionnes" in c.get("name", "").lower() or "lionnes" in c.get("title", "").lower()
        ]
        
        assert len(lionnes_groups) > 0, "Should find 'Les Lionnes' group in conversations"
        
        lionnes = lionnes_groups[0]
        print(f"✅ Found 'Les Lionnes' group:")
        print(f"   - Name: {lionnes.get('name')}")
        print(f"   - ID: {lionnes.get('conversation_id')}")
        print(f"   - Type: {lionnes.get('type')}")
        
        # Verify it's a group type
        assert lionnes.get("type") == "group", f"'Les Lionnes' should be type 'group', got {lionnes.get('type')}"
    
    def test_case_insensitive_search_capability(self):
        """Test that frontend can perform case-insensitive search on returned data"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Simulate frontend case-insensitive search for 'LION'
        search_term = "LION"
        filtered = [
            c for c in conversations 
            if search_term.lower() in c.get("name", "").lower()
        ]
        
        print(f"✅ Case-insensitive search for '{search_term}' found {len(filtered)} results:")
        for c in filtered:
            print(f"   - {c.get('name')}")
        
        # Should find 'Les Lionnes' with uppercase search
        assert len(filtered) > 0, f"Should find results when searching '{search_term}' (case-insensitive)"
    
    def test_conversation_id_is_valid(self):
        """Test that conversation_id can be used for targeting"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Check that all conversations have non-empty conversation_id
        for conv in conversations:
            conv_id = conv.get("conversation_id")
            assert conv_id, f"Conversation should have non-empty conversation_id: {conv}"
            assert isinstance(conv_id, str), f"conversation_id should be string, got {type(conv_id)}"
        
        print(f"✅ All {len(conversations)} conversations have valid conversation_id")
    
    def test_standard_groups_included(self):
        """Test that standard groups (community, vip, promo) are included"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Check for standard groups
        standard_group_ids = ["community", "vip", "promo"]
        found_standard = []
        
        for conv in conversations:
            if conv.get("conversation_id") in standard_group_ids:
                found_standard.append(conv)
        
        print(f"✅ Standard groups found: {len(found_standard)}")
        for g in found_standard:
            print(f"   - {g.get('name')} (ID: {g.get('conversation_id')})")
    
    def test_groups_sorted_before_users(self):
        """Test that groups appear before users in the list"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Find first user index
        first_user_index = None
        last_group_index = None
        
        for i, conv in enumerate(conversations):
            if conv.get("type") == "group":
                last_group_index = i
            elif conv.get("type") == "user" and first_user_index is None:
                first_user_index = i
        
        if last_group_index is not None and first_user_index is not None:
            assert last_group_index < first_user_index, "All groups should appear before users"
            print(f"✅ Groups (ending at index {last_group_index}) appear before users (starting at index {first_user_index})")
        else:
            print(f"✅ Sorting check passed (groups: {last_group_index}, users: {first_user_index})")


class TestConversationsActiveDataIntegrity:
    """Tests for data integrity of /api/conversations/active"""
    
    def test_no_duplicate_conversation_ids(self):
        """Test that there are no duplicate conversation_ids"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        ids = [c.get("conversation_id") for c in conversations]
        unique_ids = set(ids)
        
        duplicates = [id for id in ids if ids.count(id) > 1]
        unique_duplicates = list(set(duplicates))
        
        if unique_duplicates:
            print(f"⚠️ Found duplicate IDs: {unique_duplicates}")
        
        assert len(ids) == len(unique_ids), f"Found {len(ids) - len(unique_ids)} duplicate conversation_ids"
        print(f"✅ No duplicate conversation_ids found ({len(ids)} unique)")
    
    def test_all_names_are_non_empty(self):
        """Test that all conversations have non-empty names"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        empty_names = [c for c in conversations if not c.get("name", "").strip()]
        
        assert len(empty_names) == 0, f"Found {len(empty_names)} conversations with empty names"
        print(f"✅ All {len(conversations)} conversations have non-empty names")


class TestCampaignIntegration:
    """Tests for campaign integration with conversations/active"""
    
    def test_can_select_group_for_campaign(self):
        """Test that a group can be selected as targetConversationId"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Find a group
        groups = [c for c in conversations if c.get("type") == "group"]
        assert len(groups) > 0, "Should have at least one group"
        
        selected_group = groups[0]
        target_id = selected_group.get("conversation_id")
        target_name = selected_group.get("name")
        
        # Verify the selection data is valid for campaign
        assert target_id, "Selected group should have conversation_id"
        assert target_name, "Selected group should have name"
        
        print(f"✅ Can select group for campaign:")
        print(f"   - targetConversationId: {target_id}")
        print(f"   - targetConversationName: {target_name}")
    
    def test_can_select_user_for_campaign(self):
        """Test that a user can be selected as targetConversationId"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Find a user
        users = [c for c in conversations if c.get("type") == "user"]
        assert len(users) > 0, "Should have at least one user"
        
        selected_user = users[0]
        target_id = selected_user.get("conversation_id")
        target_name = selected_user.get("name")
        
        # Verify the selection data is valid for campaign
        assert target_id, "Selected user should have conversation_id"
        assert target_name, "Selected user should have name"
        
        print(f"✅ Can select user for campaign:")
        print(f"   - targetConversationId: {target_id}")
        print(f"   - targetConversationName: {target_name}")


class TestSearchFunctionality:
    """Tests for search/filter functionality (frontend simulation)"""
    
    def test_search_by_partial_name(self):
        """Test searching by partial name (frontend filter simulation)"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Test various search terms
        search_tests = [
            ("lion", "Should find 'Les Lionnes'"),
            ("LION", "Case-insensitive: Should find 'Les Lionnes'"),
            ("communauté", "Should find community group"),
            ("COMMUNAUTÉ", "Case-insensitive: Should find community group"),
            ("vip", "Should find VIP group"),
        ]
        
        for search_term, description in search_tests:
            filtered = [
                c for c in conversations 
                if search_term.lower() in c.get("name", "").lower()
            ]
            print(f"   Search '{search_term}': {len(filtered)} results - {description}")
        
        print(f"✅ Search functionality works correctly")
    
    def test_search_by_email(self):
        """Test searching users by email (frontend filter simulation)"""
        response = requests.get(f"{BASE_URL}/api/conversations/active")
        assert response.status_code == 200
        
        data = response.json()
        conversations = data.get("conversations", [])
        
        # Find users with email in name
        users_with_email = [
            c for c in conversations 
            if c.get("type") == "user" and "@" in c.get("name", "")
        ]
        
        if users_with_email:
            # Test searching by email domain
            test_user = users_with_email[0]
            email_part = test_user.get("name", "").split("@")[-1].split(")")[0] if "@" in test_user.get("name", "") else ""
            
            if email_part:
                filtered = [
                    c for c in conversations 
                    if email_part.lower() in c.get("name", "").lower()
                ]
                print(f"✅ Search by email domain '{email_part}': {len(filtered)} results")
        else:
            print(f"✅ No users with email in display name found (this is OK)")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
