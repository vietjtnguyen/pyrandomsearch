#!/usr/bin/env python3
def generate_new_point(point, radii):
    import math
    import random

    dimensionality = len(point) - 1
    delta = tuple(random.gauss(0, 1) for i in range(dimensionality))
    delta_norm = math.sqrt(sum(x ** 2 for x in delta))
    new_point = [None]
    new_point.extend(
        point[i + 1] + x / delta_norm * radii[i]
        for i, x in enumerate(delta)
    )
    return new_point


def run_eval_process(point, command_format_string):
    import shlex
    import subprocess

    command = shlex.split(command_format_string.format(*point[1:]))
    return subprocess.Popen(
        command,
        stdin=None,
        stdout=subprocess.PIPE,
        universal_newlines=True)


def handle_eval_results(existing_points, new_point, proc, print_func):
    import sys

    stdout, stderr = proc.communicate()

    for line in stdout.split('\n'):
        if line.startswith('#'):
            continue
        try:
            new_point[0] = float(line)
        except:
            continue

    if new_point[0] is None:
        print_func(
            '## ERROR: Could not find evaluated point value in process '
            'output.')
        new_point[0] = 'nan'
        print_func(' '.join(map(str, new_point)))
        sys.exit(1)

    existing_points.append(new_point)
    print_func(' '.join(map(str, new_point)))
    sys.stdout.flush()


def main():
    import argparse
    import ast
    from datetime import datetime
    import math
    import random
    import sys

    parser = argparse.ArgumentParser(
        description='''
            Performs random search on a parameter space where the objective
            function is a program that outputs a number to stdout. The initial
            points are read from the input specified by --evaluated-points
            (default is stdin). At each step the set of existing points is
            sorted to find the "best" point (see --optimization-type).
            Exploratory points (see --num-proposals) are then generated by
            picking an offset vector on a scaled N-dimensional sphere (see
            --dimensionality and --radii) and applying it to the best point.
            For each exploratory point the command is run to evaluate that
            point. Each newly evaluated point is added back to the set of
            existing points and the optimization repeats until convergence (see
            --stale-threshold and --stale-count). The value for a point is the
            first line in the command's stdout that can be converted to a
            float. This means the string 'inf' and '-inf' are parsable and can
            be used to mark impossible parameter points.''')
    parser.add_argument(
        '-d', '--dimensionality',
        default=None, type=int,
        help='''
            dimensionality of the parameter space (default: infer from
            --evaluated-points input)''')
    parser.add_argument(
        '-r', '--radii',
        default='1',
        help='''
            defines the radii at each dimension to scale the "exploration
            sphere" by; last value is used if dimensionality is too small; for
            example, if "1,2,3" was specified for a four dimensional problem
            then the exploration sphere is scaled by "1,2,3,3" (default: 1)''')
    parser.add_argument(
        '-R', '--rng-seed',
        default=None, type=int,
        help='''
            pseudo random number generator seed (default: random)''')
    parser.add_argument(
        '-i', '--input',
        default='-',
        help='''
            file that contains a list of already evaluated points; the file
            format should be white space delimited (leading # are ignored) with
            the first number being the score/cost and each subsequent number
            being a coordinate for that point in the parameter space (default:
            '-' meaning stdin)''')
    parser.add_argument(
        '-a', '--append',
        action='store_true', default=False,
        help='''
            after the input is read for existing evaluated points it is
            re-opened in append mode so that newly evaluated points are
            appended to the file; this allows for a sort of "in place"
            operation where the same optimization continually uses the same
            file (default: do not append)''')
    parser.add_argument(
        '-O', '--optimization-type',
        choices={'min', 'max'}, default='min',
        help='''
            defines the type of optimization: min or max (default: min)''')
    parser.add_argument(
        '-t', '--stale-threshold',
        default=0.0, type=float,
        help='''
            if the change between the last best value and the current best
            value is less than or equal to this threshold then the values are
            considered stale (default: 0.0)''')
    parser.add_argument(
        '-c', '--stale-count',
        default=10, type=int,
        help='''
            when there are --stale-count consecutive stale steps (see
            --stale-threshold) then the optimization is stopped and considered
            complete (default: 10)''')
    parser.add_argument(
        '-p', '--num-proposals',
        default=1, type=int,
        help='''
            the number of "exploratory point" proposals to generate and
            evaluate in parallel during each step; all exploratory points will
            be offset from the same "best point" for that step (default: 1)''')
    parser.add_argument(
        '--print-date-and-time',
        action='store_true', default=False,
        help='''
            prints the current date and time in ISO format before each step''')
    parser.add_argument(
        'command',
        type=str,
        help='''
            defines the command to run to evaluate the objective function; the
            command is expected to return the score/cost via stdout as the
            first line that can be converted to a floating point number (lines
            beginning with a hash are ignored); the parameters are inserted
            into the command via Python string formatting; for example, if we
            are optimizing a two dimensional parameter space and random search
            wants to evaluate the parameters (1.2, 3.4) and the command string
            is set to './my_expensive_eval --alpha {1} -C {2}' the the command
            that random search will invoke is './my_expensive_eval --alpha 1.2
            -C 3.4'; note that the resulting command string is split using
            shlex.split() after the parameters are inserted''')

    args = parser.parse_args()

    if args.dimensionality is not None and args.dimensionality < 1:
        print('## ERROR: --dimensionality must be greater than zero')
        sys.exit(1)
    if args.stale_threshold < 0:
        print('## ERROR: --stale-threshold must be positive')
        sys.exit(1)
    if args.stale_count < 1:
        print('## ERROR: --stale-count must be greater than zero')
        sys.exit(1)
    if args.num_proposals < 1:
        print('## ERROR: --num-proposals must be greater than zero')
        sys.exit(1)

    sort_reverse = (args.optimization_type == 'min')

    random.seed(args.rng_seed)

    if args.input == '-':
        input_stream = sys.stdin
    else:
        input_stream = open(args.input, 'r')

    existing_points = [
        tuple(map(float, x.split()))
        for x in map(str.strip, input_stream.readlines())
        if not x.startswith('#') and not len(x) == 0
    ]

    if len(existing_points) == 0:
        print('## WARN: No existing points, seeding with origin')
        if args.dimensionality is None:
            print(
                '## ERROR: No existing points to infer dimensionality and '
                '--dimensionality is not specified, cannot seed '
                'optimization')
            sys.exit(1)
    else:
        # Infer dimensionality if one is not specified
        if args.dimensionality is None:
            args.dimensionality = len(existing_points[0]) - 1

    for i, point in enumerate(existing_points):
        if len(point) == 0:
            print(
                '## ERROR: Encountered empty point (point #{}) in existing '
                'points input.'.format(i))
            sys.exit(1)
        if len(point) == 1:
            print(
                '## ERROR: Encountered point with score but no parameters '
                '(point #{}) in existing points input.'.format(i))
            sys.exit(1)
        if len(point) - 1 != args.dimensionality:
            print(
                '## ERROR: Encountered point with mismatched dimensionality '
                '(point #{}) in existing points input.'.format(i))
            sys.exit(1)

    radii = list(eval(args.radii + ',', {'math': math}))
    radii.extend([radii[-1]] * (args.dimensionality - len(radii)))

    print('## Existing points:')
    existing_points.sort(key=lambda x: x[0], reverse=sort_reverse)
    for point in existing_points:
        print(' '.join(map(str, point)))
    print('## New points:')

    if args.append:
        append_stream = open(args.input, 'a')
        def print_output(x):
            print(x, file=append_stream)
            print(x)
    else:
        def print_output(x):
            print(x)

    sys.stdout.flush()
    last_best_value = float('-inf') if sort_reverse else float('inf')
    num_stale_steps = 0
    while True:

        if args.print_date_and_time:
            print_output(
                '## Date and time: {}'.format(
                    datetime.isoformat(datetime.now())))

        existing_points.sort(key=lambda x: x[0], reverse=sort_reverse)

        # Get the best existing point if there is one
        if len(existing_points) == 0:
            # If there isn't then use the origin
            best_existing_point = [
                float('-inf') if sort_reverse else float('inf')
            ]
            best_existing_point.extend([0] * args.dimensionality)
        else:
            best_existing_point = existing_points[-1]

        # Check if our best value is changing and if we're reached stale
        # convergence
        best_value_change = abs(best_existing_point[0] - last_best_value)
        if best_value_change <= args.stale_threshold:
            num_stale_steps += 1
        if num_stale_steps >= args.stale_count:
            print_output(
                '## Best point: {}'.format(
                    ' '.join(map(str, best_existing_point))))
            break
        last_best_value = best_existing_point[0]

        # Collect the new points and their evaluation processes
        new_point_evals = []
        for i in range(args.num_proposals):
            new_point = generate_new_point(
                best_existing_point,
                radii)
            proc = run_eval_process(new_point, args.command)
            new_point_evals.append((new_point, proc))

        # Wait for and obtain each new points' evaluation results
        for new_point, proc in new_point_evals:
            handle_eval_results(existing_points, new_point, proc, print_output)


if __name__ == '__main__':
    main()
