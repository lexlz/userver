#pragma once

/// @file utils/datetime/date.hpp
/// @brief @copybrief utils::datetime::Date

#include <chrono>
#include <iosfwd>
#include <stdexcept>
#include <string>

#include <formats/common/meta.hpp>

namespace logging {
class LogHelper;
}

namespace utils::datetime {

/// @brief Date in format YYYY-MM-DD, std::chrono::year_month_day like type.
///
/// Convertible to std::sys_days and could be constructed from year,
/// month and day integers.
class Date final {
 public:
  using Days = std::chrono::duration<long long, std::ratio<86400>>;
  using SysDays = std::chrono::time_point<std::chrono::system_clock, Days>;

  Date() noexcept = default;
  Date(const Date&) noexcept = default;
  Date& operator=(const Date&) noexcept = default;

  /// @brief Constructs Date without validation of input arguments
  Date(int year, int month, int day);

  // TODO: remove after TAXICOMMON-3633
  [[deprecated(
      "Do not use! Use the Date(SysDays tp) constructor "
      "instead")]] constexpr explicit Date(std::chrono::system_clock::time_point
                                               tp)
      : sys_days_(std::chrono::time_point_cast<Days>(tp)) {}

  /// @brief constructor from system clock time point in days.
  constexpr Date(SysDays tp) noexcept : sys_days_(tp) {}

  /// @brief Returns a time point corresponding to the date.
  ///
  /// This function may return the same time point, that was passed to
  /// constructor.
  SysDays GetSysDays() const { return sys_days_; }

  /// @copydoc GetSysDays()
  constexpr explicit operator SysDays() const { return sys_days_; }

  // TODO: remove after TAXICOMMON-3633
  [[deprecated("Use GetSysDays() instead")]] SysDays GetUnderlying() const {
    return sys_days_;
  }

  bool operator==(Date other) const { return sys_days_ == other.sys_days_; }
  bool operator!=(Date other) const { return !(*this == other); }

 private:
  SysDays sys_days_{};
};

/// Validates date_string and constructs date from YYYY-MM-DD string and
Date DateFromRFC3339String(const std::string& date_string);

/// Outputs date as a YYYY-MM-DD string
std::string ToString(Date date);

template <typename Value>
std::enable_if_t<formats::common::kIsFormatValue<Value>, Date> Parse(
    const Value& value, formats::parse::To<Date>) {
  std::string str;
  try {
    str = value.template As<std::string>();
  } catch (const std::exception& e) {
    throw typename Value::ParseException(
        "Only strings can be parsed as `utils::datetime::Date`");
  }

  try {
    return utils::datetime::DateFromRFC3339String(str);
  } catch (const std::exception& e) {
    throw typename Value::ParseException(
        "'" + str + "' cannot be parsed to `utils::datetime::Date`");
  }
}

template <typename Value>
std::enable_if_t<formats::common::kIsFormatValue<Value>, Value> Serialize(
    Date date, formats::serialize::To<Value>) {
  return typename Value::Builder(ToString(date)).ExtractValue();
}

template <typename StringBuilder>
void WriteToStream(Date value, StringBuilder& sw) {
  WriteToStream(ToString(value), sw);
}

template <class LogHelper>
std::enable_if_t<std::is_same_v<LogHelper, logging::LogHelper>, LogHelper&>
operator<<(LogHelper& lh, Date date) {
  // This function was made template to work well with forward
  // declared logging::LogHelper

  return lh << ToString(date);
}

std::ostream& operator<<(std::ostream& os, Date date);

}  // namespace utils::datetime
