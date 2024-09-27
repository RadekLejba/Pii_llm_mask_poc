from fastapi.testclient import TestClient
from main import app
from api.generate_answer.mask import PII_Mask

client = TestClient(app)


class TestPIIMask:
    def test_mask_finds_universal_data(self):
        """
        This will test if the PII_Mask class can find universaly recognized
        PII data, such as email addresses and credit card numbers.
        """
        unmasked_text = (
            "Hello, my email is johndoe@gmail.com and my friend's email is"
            " sarah.connor@someotherdomain.pl, our credit card numbers are"
            " 1234-5678-1234-5678 and 1234567812345678."
            " We also have phone numbers: +27 21 123 4567 and +11491570129"
        )

        mask = PII_Mask(unmasked_text)

        assert len(mask.matches_map["email"]) == 2
        assert "johndoe@gmail.com" in mask.matches_map["email"]
        assert "sarah.connor@someotherdomain.pl" in mask.matches_map["email"]
        assert len(mask.matches_map["credit_card"]) == 2
        assert "1234-5678-1234-5678" in mask.matches_map["credit_card"]
        assert "1234567812345678" in mask.matches_map["credit_card"]
        assert len(mask.matches_map["phone_number"]) == 2
        assert "+27 21 123 4567 " in mask.matches_map["phone_number"]
        assert "+11491570129" in mask.matches_map["phone_number"]

    def test_mask_finds_ner_data(self):
        """
        This will test if the PII_Mask class can filter out user names
        and organizations.
        """
        unmasked_text = (
            "Hello, my name is John Doe and I work for Dune Spice Mining Industries. My friend"
            " is Sarah Connor and she works for AI Supremacy Inc."
        )
        mask = PII_Mask(unmasked_text)

        assert len(mask.matches_map["name"]) == 2
        assert "John Doe" in mask.matches_map["name"]
        assert "Sarah Connor" in mask.matches_map["name"]
        assert len(mask.matches_map["organization"]) == 2
        assert "Dune Spice Mining Industries" in mask.matches_map["organization"]
        assert "AI Supremacy Inc." in mask.matches_map["organization"]

    def test_masked_text(self):
        """
        This will test if the PII_Mask class can mask the PII data.
        """
        unmasked_text = (
            "Hello, my email is radek.lejba@gmail.com, my credit card number is"
            " 1234-5678-1234-5678, my phone number is +48 123 456 789, my name is"
            " Radek Lejba and I work for AI Supremacy Inc."
        )
        mask = PII_Mask(unmasked_text)

        assert "radek.lejba@gmail.com" not in mask.masked_text
        assert "1234-5678-1234-5678" not in mask.masked_text
        assert "+48 123 456 789" not in mask.masked_text
        assert "Radek Lejba" not in mask.masked_text
        assert "AI Supremacy Inc." not in mask.masked_text
        assert mask.masked_map["radek.lejba@gmail.com"] != "radek.lejba@gmail.com"
        assert mask.masked_map["radek.lejba@gmail.com"] in mask.masked_text
        assert mask.masked_map["1234-5678-1234-5678"] != "1234-5678-1234-5678"
        assert mask.masked_map["1234-5678-1234-5678"] in mask.masked_text
        assert mask.masked_map["+48 123 456 789"] != "+48 123 456 789"
        assert mask.masked_map["+48 123 456 789"] in mask.masked_text
        assert mask.masked_map["Radek Lejba"] != "Radek Lejba"
        assert mask.masked_map["Radek Lejba"] in mask.masked_text
        assert mask.masked_map["AI Supremacy Inc."] != "AI Supremacy Inc."
        assert mask.masked_map["AI Supremacy Inc."] in mask.masked_text

    def test_unmask(self):
        """
        Test if the PII_Mask class can unmask the text received from the LLM model.
        """
        unmasked_text = (
            "Hello, my email is radek.lejba@gmail.com, my credit card number is"
            " 1234-5678-1234-5678, my phone number is +48 123 456 789, my name is"
            " Radek Lejba and I work for AI Supremacy Inc."
        )
        mask = PII_Mask(unmasked_text)
        masked_response = (
            f"Mocked response from the LLM model, user email is {mask.masked_map['radek.lejba@gmail.com']},"
            f" user credit card number is {mask.masked_map['1234-5678-1234-5678']}, user phone number is"
            f" {mask.masked_map['+48 123 456 789']}, user name is {mask.masked_map['Radek Lejba']} and"
            f" user works for {mask.masked_map['AI Supremacy Inc.']}"
        )

        unmasked_response = mask.unmask(masked_response)

        assert unmasked_response == (
            "Mocked response from the LLM model, user email is radek.lejba@gmail.com, "
            "user credit card number is 1234-5678-1234-5678, user phone number is +48 123 "
            "456 789, user name is Radek Lejba and user works for AI Supremacy Inc."
        )
