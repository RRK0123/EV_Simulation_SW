#pragma once

#include <cstdint>

#ifdef _WIN32
#define EVSIM_API __declspec(dllexport)
#else
#define EVSIM_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void* evsim_orchestrator_handle;

EVSIM_API evsim_orchestrator_handle evsim_create_orchestrator();
EVSIM_API void evsim_destroy_orchestrator(evsim_orchestrator_handle handle);
EVSIM_API int evsim_run_default_scenario(evsim_orchestrator_handle handle, double time_step, std::uint32_t steps);

#ifdef __cplusplus
}
#endif

