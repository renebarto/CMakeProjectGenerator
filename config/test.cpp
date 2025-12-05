{header}

#include "gtest/gtest.h"

#include "{libname}/{libname}.h"

namespace {namespace} {
namespace test {

class {class} : public ::testing::Test
{
public:
    {class}()
    {}
    {class}(const {class} &) = delete;
    {class}({class} &&) = delete;
    {class} operator =(const {class} &) = delete;
    {class} operator =({class} &&) = delete;

    void SetUp() override
    {
    }
    void TearDown() override
    {
    }
};

TEST_F({class}, fails_always)
{
    FAIL();
}

} // namespace test
} // namespace {namespace}
