"""
Tests for SCATEX (SCATE eXecutable) output from dateparser.

These tests verify that dateparser correctly parses date strings and returns
SCATEX compositional expressions instead of datetime objects.
"""

import pytest
from datetime import datetime

import dateparser
from dateparser.scatex import (
    TemporalExpression,
    Year, Month, Day, Hour, Minute, Second,
    DayOfWeek, DayOfWeekType, MonthOfYear, MonthOfYearType,
    Repeating, Unit,
    This, Last, Next, Shift, Period, Direction,
    Today, Yesterday, Tomorrow, Now, Unknown,
)


class TestAbsoluteDates:
    """Tests for parsing absolute date strings."""
    
    def test_full_date(self):
        """Test parsing a complete date (day, month, year)."""
        result = dateparser.parse("October 7, 2023", languages=['en'])
        assert isinstance(result, Day)
        assert result.day == 7
        assert result.month == 10
        assert result.year == 2023
    
    def test_month_year(self):
        """Test parsing a month and year (no day)."""
        result = dateparser.parse("March 2015", languages=['en'])
        assert isinstance(result, Month)
        assert result.month == 3
        assert result.year == 2015
    
    def test_year_only(self):
        """Test parsing just a year."""
        result = dateparser.parse("2014", languages=['en'])
        assert isinstance(result, Year)
        assert result.digits == 2014
    
    def test_partial_date_no_year(self):
        """Test parsing a date without year (partial)."""
        result = dateparser.parse("October 7", languages=['en'])
        assert isinstance(result, Day)
        assert result.day == 7
        assert result.month == 10
        assert result.year is None  # Partial - year unknown
    
    def test_time_only(self):
        """Test parsing just a time."""
        result = dateparser.parse("15:30", languages=['en'])
        assert isinstance(result, Minute)
        assert result.hour == 15
        assert result.minute == 30


class TestRelativeDates:
    """Tests for parsing relative date strings."""
    
    def test_days_ago(self):
        """Test parsing '3 days ago'."""
        result = dateparser.parse("3 days ago", languages=['en'])
        assert isinstance(result, Shift)
        assert isinstance(result.interval, Today)
        assert result.period.unit == Unit.DAY
        assert result.period.value == 3
        assert result.direction == Direction.BEFORE
    
    def test_yesterday(self):
        """Test parsing 'yesterday'."""
        result = dateparser.parse("yesterday", languages=['en'])
        assert isinstance(result, Yesterday)
    
    def test_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = dateparser.parse("tomorrow", languages=['en'])
        assert isinstance(result, Tomorrow)
    
    def test_today(self):
        """Test parsing 'today'."""
        result = dateparser.parse("today", languages=['en'])
        assert isinstance(result, Today)
    
    def test_now(self):
        """Test parsing 'now'."""
        result = dateparser.parse("now", languages=['en'])
        assert isinstance(result, Now)


class TestNextLastThis:
    """Tests for next/last/this patterns."""
    
    def test_next_monday(self):
        """Test parsing 'next Monday'."""
        result = dateparser.parse("next Monday", languages=['en'])
        assert isinstance(result, Next)
        assert isinstance(result.interval, DayOfWeek)
        assert result.interval.type == DayOfWeekType.MONDAY
    
    def test_last_friday(self):
        """Test parsing 'last Friday'."""
        result = dateparser.parse("last Friday", languages=['en'])
        assert isinstance(result, Last)
        assert isinstance(result.interval, DayOfWeek)
        assert result.interval.type == DayOfWeekType.FRIDAY
    
    def test_last_week(self):
        """Test parsing 'last week'."""
        result = dateparser.parse("last week", languages=['en'])
        assert isinstance(result, Last)
        assert isinstance(result.interval, Repeating)
        assert result.interval.unit == Unit.WEEK
    
    def test_this_week(self):
        """Test parsing 'this week'."""
        result = dateparser.parse("this week", languages=['en'])
        assert isinstance(result, This)
        assert isinstance(result.interval, Repeating)
        assert result.interval.unit == Unit.WEEK
    
    def test_last_month(self):
        """Test parsing 'last month'."""
        result = dateparser.parse("last month", languages=['en'])
        assert isinstance(result, Last)
        assert isinstance(result.interval, Repeating)
        assert result.interval.unit == Unit.MONTH
    
    def test_this_year(self):
        """Test parsing 'this year'."""
        result = dateparser.parse("this year", languages=['en'])
        assert isinstance(result, This)
        assert isinstance(result.interval, Repeating)
        assert result.interval.unit == Unit.YEAR


class TestEvaluation:
    """Tests for evaluating SCATEX expressions with an anchor date."""
    
    @pytest.fixture
    def anchor(self):
        """Provide a fixed anchor date for testing."""
        return datetime(2023, 10, 15, 12, 0, 0)
    
    def test_evaluate_absolute_date(self, anchor):
        """Test evaluating an absolute date."""
        result = dateparser.parse("October 7, 2023", languages=['en'])
        start, end = result.evaluate(anchor)
        assert start == datetime(2023, 10, 7, 0, 0, 0)
        assert end == datetime(2023, 10, 7, 23, 59, 59)
    
    def test_evaluate_days_ago(self, anchor):
        """Test evaluating '3 days ago'."""
        result = dateparser.parse("3 days ago", languages=['en'])
        start, end = result.evaluate(anchor)
        # 3 days before Oct 15 = Oct 12
        assert start == datetime(2023, 10, 12, 0, 0, 0)
        assert end == datetime(2023, 10, 12, 23, 59, 59)
    
    def test_evaluate_yesterday(self, anchor):
        """Test evaluating 'yesterday'."""
        result = dateparser.parse("yesterday", languages=['en'])
        start, end = result.evaluate(anchor)
        # Yesterday from Oct 15 = Oct 14
        assert start == datetime(2023, 10, 14, 0, 0, 0)
        assert end == datetime(2023, 10, 14, 23, 59, 59)
    
    def test_evaluate_tomorrow(self, anchor):
        """Test evaluating 'tomorrow'."""
        result = dateparser.parse("tomorrow", languages=['en'])
        start, end = result.evaluate(anchor)
        # Tomorrow from Oct 15 = Oct 16
        assert start == datetime(2023, 10, 16, 0, 0, 0)
        assert end == datetime(2023, 10, 16, 23, 59, 59)
    
    def test_evaluate_next_monday(self, anchor):
        """Test evaluating 'next Monday'."""
        result = dateparser.parse("next Monday", languages=['en'])
        start, end = result.evaluate(anchor)
        # Oct 15, 2023 is Sunday, so next Monday is Oct 16
        assert start == datetime(2023, 10, 16, 0, 0, 0)
        assert end == datetime(2023, 10, 16, 23, 59, 59)
    
    def test_evaluate_partial_date(self, anchor):
        """Test that partial dates cannot be evaluated without anchor year."""
        result = dateparser.parse("October 7", languages=['en'])
        assert isinstance(result, Day)
        assert result.year is None
        # Evaluation should return (None, None) for partial dates
        start, end = result.evaluate(anchor)
        assert start is None
        assert end is None


class TestMultiLanguage:
    """Tests for multi-language support."""
    
    def test_spanish_days_ago(self):
        """Test parsing Spanish relative date."""
        result = dateparser.parse("hace 3 días", languages=['es'])
        assert isinstance(result, Shift)
        assert result.period.unit == Unit.DAY
        assert result.period.value == 3
        assert result.direction == Direction.BEFORE
    
    def test_french_date(self):
        """Test parsing French date."""
        result = dateparser.parse("7 octobre 2023", languages=['fr'])
        assert isinstance(result, Day)
        assert result.day == 7
        assert result.month == 10
        assert result.year == 2023


class TestEdgeCases:
    """Tests for edge cases and special handling."""
    
    def test_none_for_unparseable(self):
        """Test that unparseable strings return None."""
        result = dateparser.parse("this is not a date")
        assert result is None
    
    def test_empty_string(self):
        """Test that empty strings return None."""
        result = dateparser.parse("")
        assert result is None
    
    def test_scatex_data_class(self):
        """Test the ScatexData wrapper class."""
        from dateparser.date import DateDataParser
        
        parser = DateDataParser(languages=['en'])
        data = parser.get_scatex_data("October 7, 2023")
        
        assert data.scatex_expr is not None
        assert data.period == "day"
        assert data.locale == "en"
        
        # Test evaluate method on ScatexData
        anchor = datetime(2023, 10, 15)
        start, end = data.evaluate(anchor)
        assert start == datetime(2023, 10, 7, 0, 0, 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
