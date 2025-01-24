from enum import Enum
from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


class FilterType(str, Enum):
    """Enumeration of all available filter types for people search in Crustdata.

    These filters can be used to narrow down search results based on various professional attributes.
    """

    CURRENT_COMPANY = "CURRENT_COMPANY"
    CURRENT_TITLE = "CURRENT_TITLE"
    PAST_TITLE = "PAST_TITLE"
    COMPANY_HEADQUARTERS = "COMPANY_HEADQUARTERS"
    COMPANY_HEADCOUNT = "COMPANY_HEADCOUNT"
    REGION = "REGION"
    PROFILE_LANGUAGE = "PROFILE_LANGUAGE"
    YEARS_AT_CURRENT_COMPANY = "YEARS_AT_CURRENT_COMPANY"
    YEARS_IN_CURRENT_POSITION = "YEARS_IN_CURRENT_POSITION"
    YEARS_OF_EXPERIENCE = "YEARS_OF_EXPERIENCE"
    PAST_COMPANY = "PAST_COMPANY"
    COMPANY_TYPE = "COMPANY_TYPE"
    KEYWORD = "KEYWORD"


class CompanyHeadcount(str, Enum):
    """Enumeration of company size ranges based on employee count. Used for filtering companies by their workforce size."""

    SELF_EMPLOYED = "Self-employed"
    SIZE_1_10 = "1-10"
    SIZE_11_50 = "11-50"
    SIZE_51_200 = "51-200"
    SIZE_201_500 = "201-500"
    SIZE_501_1000 = "501-1,000"
    SIZE_1001_5000 = "1,001-5,000"
    SIZE_5001_10000 = "5,001-10,000"
    SIZE_10001_PLUS = "10,001+"


class ProfileLanguage(str, Enum):
    """Enumeration of available profile languages. Used to filter profiles based on their primary language setting."""

    ARABIC = "Arabic"
    ENGLISH = "English"
    SPANISH = "Spanish"
    PORTUGUESE = "Portuguese"
    CHINESE = "Chinese"
    FRENCH = "French"
    ITALIAN = "Italian"
    RUSSIAN = "Russian"
    GERMAN = "German"
    DUTCH = "Dutch"
    TURKISH = "Turkish"
    TAGALOG = "Tagalog"
    POLISH = "Polish"
    KOREAN = "Korean"
    JAPANESE = "Japanese"
    MALAY = "Malay"
    NORWEGIAN = "Norwegian"
    DANISH = "Danish"
    ROMANIAN = "Romanian"
    SWEDISH = "Swedish"
    BAHASA_INDONESIA = "Bahasa Indonesia"
    CZECH = "Czech"


class YearsRange(str, Enum):
    """Enumeration of experience duration ranges.

    Used for filtering based on years of experience in various contexts.
    """

    LESS_THAN_1 = "Less than 1 year"
    ONE_TO_TWO = "1 to 2 years"
    THREE_TO_FIVE = "3 to 5 years"
    SIX_TO_TEN = "6 to 10 years"
    MORE_THAN_10 = "More than 10 years"


class FilterOperationType(str, Enum):
    """Enumeration of filter operation types.

    Defines how the filter values should be applied in the search.
    """

    IN = "in"  # Include profiles matching the filter values
    NOT_IN = "not in"  # Exclude profiles matching the filter values


class TextFilter(BaseModel):
    """Model for text-based filters in people search. Used for filters that require string values or predefined options."""

    filter_type: FilterType = Field(
        ..., description="The type of filter to apply to the search"
    )
    type: FilterOperationType = Field(
        ..., description="The operation type for the filter (inclusion or exclusion)"
    )
    value: List[str] = Field(
        ...,
        description="List containing a single filter value. Must contain exactly one item",
    )

    @field_validator("value")
    def validate_filter_value(cls, v: List[str], info) -> List[str]:
        """Validate filter values based on filter type. Provides detailed error messages with valid options for enum-based filters."""
        filter_type = info.data.get("filter_type")
        if not filter_type:
            return v

        # Define filters that allow multiple values
        multi_value_filters = {
            FilterType.KEYWORD,
            FilterType.CURRENT_COMPANY,
            FilterType.PAST_COMPANY,
            FilterType.CURRENT_TITLE,
            FilterType.PAST_TITLE,
        }

        # Validate list length based on filter type
        if filter_type not in multi_value_filters and len(v) != 1:
            raise ValueError(
                f"Filter type {filter_type} must contain exactly one value"
            )

        # For single-value filters, validate the value
        if filter_type not in multi_value_filters:
            value = v[0]

            # Validate enum-specific values with detailed error messages
            if filter_type == FilterType.COMPANY_HEADCOUNT:
                valid_options = [e.value for e in CompanyHeadcount]
                if value not in valid_options:
                    error_msg = (
                        f"Invalid company headcount value: '{value}'\n"
                        f"Valid options are:\n- " + "\n- ".join(valid_options)
                    )
                    raise ValueError(error_msg)

            elif filter_type == FilterType.PROFILE_LANGUAGE:
                valid_options = [e.value for e in ProfileLanguage]
                if value not in valid_options:
                    error_msg = (
                        f"Invalid profile language value: '{value}'\n"
                        f"Valid options are:\n- " + "\n- ".join(valid_options)
                    )
                    raise ValueError(error_msg)

            elif filter_type in [
                FilterType.YEARS_AT_CURRENT_COMPANY,
                FilterType.YEARS_IN_CURRENT_POSITION,
                FilterType.YEARS_OF_EXPERIENCE,
            ]:
                valid_options = [e.value for e in YearsRange]
                if value not in valid_options:
                    error_msg = (
                        f"Invalid years range value: '{value}' for filter type {filter_type}\n"
                        f"Valid options are:\n- " + "\n- ".join(valid_options)
                    )
                    raise ValueError(error_msg)

        return v


class PeopleSearchFilter(BaseModel):
    """Main model for constructing people search filters in Crustdata."""

    filters: List[TextFilter] = Field(
        ..., description="List of filters to apply to the search."
    )

    class Config:
        """Configuration for the PeopleSearchFilter model."""

        use_enum_values = True
