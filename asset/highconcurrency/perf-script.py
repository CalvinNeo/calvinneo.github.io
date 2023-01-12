from collections import defaultdict
start_time=defaultdict(defaultdict)

def trace_unhandled(event_name, context, event_fields_dict, perf_sample_dict):
        common_comm=event_fields_dict["common_comm"]
        common_secs=event_fields_dict["common_s"]
        common_nsecs=event_fields_dict["common_ns"]

        tid=perf_sample_dict['sample']["tid"]

        if event_name.endswith("__return"):
                print(event_name)
                if not start_time[event_name[:-8]].has_key(tid):
                        return
                now=common_secs * 1000000000 + common_nsecs
                duration=float(now - start_time[event_name[:-8]][tid]) / 1000000
                print(common_comm + " " + event_name + " runtime: " + str(duration) + "ms")
        else:
                start=(common_secs * 1000000000) + common_nsecs
                start_time[event_name][tid]=start