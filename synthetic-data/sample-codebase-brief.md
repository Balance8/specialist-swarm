# Codebase Brief — Tracer (synthetic)

**What it is:** Tracer is an open-source library that adds production observability
*inside* your deploy pipeline instead of beside it. You wrap your deploy command;
Tracer instruments the release and watches it for the first 10 minutes.

## The problem we kept hitting

Small teams ship fast, then lose Friday afternoons firefighting. The error shows up
in production, but the dashboards that would explain it were never wired to *this*
release. By the time someone correlates the spike to the deploy, an hour is gone.

## What teams do today

The standard move is to bolt on monitoring after the fact: Datadog for metrics,
Sentry for errors, a log aggregator, a status page, and a hand-built Grafana board.
Five tools, five integrations, five places to look. Each is good. None of them know
that a deploy just happened, so nobody connects the regression to the change that
caused it until a human does it manually.

## The Tracer insight

A deploy already knows the exact moment of change and the exact diff that shipped.
Tracer treats the deploy itself as the observability anchor. It tags every metric,
error, and log line with the release SHA, holds a 10-minute watch window, and if the
error rate or latency crosses the pre-deploy baseline, it auto-annotates the offending
endpoints and links straight to the lines in the diff.

## How it comes together

`tracer deploy ./ship.sh` — that's the whole setup. You ship like normal. If something
regresses, Tracer tells you what broke, which commit broke it, and which endpoints are
affected, in one message, before you've even opened a dashboard. Mean-time-to-diagnosis
in our pilot dropped from 47 minutes to under 4.

## Stack
Rust core, language SDKs for Node/Python/Go, OTLP-compatible export so it drops into
existing backends. MIT licensed. ~6k lines.
