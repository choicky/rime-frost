#include <rime_api.h>

#include <cstdlib>
#include <cstring>
#include <iostream>

namespace {

void require(bool condition, const char* message) {
  if (!condition) {
    std::cerr << "FAIL: " << message << '\n';
    std::exit(EXIT_FAILURE);
  }
}

void expect_schema(RimeSessionId session, const char* expected) {
  char schema[128]{};
  require(rime_get_api()->get_current_schema(session, schema, sizeof(schema)),
          "could not read current schema");
  require(std::strcmp(schema, expected) == 0, "unexpected current schema");
}

void expect_input(RimeSessionId session, const char* keys) {
  auto* api = rime_get_api();
  for (; *keys; ++keys) {
    require(api->process_key(session, *keys, 0), "input key was not handled");
  }

  RimeCandidateListIterator list{};
  require(api->candidate_list_begin(session, &list), "no candidates");
  int index = -1;
  while (api->candidate_list_next(&list)) {
    if (std::strcmp(list.candidate.text, "你好") == 0) {
      index = list.index;
      break;
    }
  }
  api->candidate_list_end(&list);
  require(index >= 0, "expected candidate 你好 is missing");
  require(api->select_candidate(session, index), "candidate selection failed");

  RIME_STRUCT(RimeCommit, commit);
  require(api->get_commit(session, &commit), "candidate did not commit");
  require(std::strcmp(commit.text, "你好") == 0, "wrong candidate committed");
  api->free_commit(&commit);
}

}  // namespace

int main(int argc, char** argv) {
  require(argc == 3, "usage: smoke-test SHARED_DATA_DIR USER_DATA_DIR");
  auto* api = rime_get_api();
  RIME_STRUCT(RimeTraits, traits);
  traits.shared_data_dir = argv[1];
  traits.user_data_dir = argv[2];
  traits.app_name = "rime.frost_custom_smoke";
  traits.min_log_level = 2;
  api->setup(&traits);
  api->initialize(&traits);
  require(api->start_maintenance(True), "could not start deployment");
  api->join_maintenance_thread();

  const char* natural_code = "rime_frost_double_pinyin";
  const char* full_pinyin = "rime_frost";
  RimeSchemaList menu{};
  require(api->get_schema_list(&menu), "could not read schema menu");
  require(menu.size == 2, "expected exactly two schemas");
  require(std::strcmp(menu.list[0].schema_id, natural_code) == 0 &&
              std::strcmp(menu.list[1].schema_id, full_pinyin) == 0,
          "expected Natural Code followed by Full Pinyin");
  api->free_schema_list(&menu);

  auto session = api->create_session();
  require(session, "could not start a clean Rime session");
  expect_schema(session, natural_code);
  api->set_option(session, "traditionalization", False);
  expect_input(session, "nihk");
  require(api->select_schema(session, full_pinyin), "could not switch to Full Pinyin");
  expect_schema(session, full_pinyin);
  api->set_option(session, "traditionalization", False);
  expect_input(session, "nihao");
  api->destroy_session(session);
  api->finalize();
  std::cout << "Natural Code and Full Pinyin deployment and input passed\n";
}
