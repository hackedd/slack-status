package main

import (
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/slack-go/slack"
	"github.com/urfave/cli"
)

func connect(c *cli.Context) (*slack.Client, *slack.AuthTestResponse, error) {
	verbose := c.GlobalBool("verbose")
	token := c.GlobalString("token")

	if token == "" {
		return nil, nil, fmt.Errorf("no token specified")
	}

	client := slack.New(token, slack.OptionDebug(verbose))

	authTest, err := client.AuthTest()
	if err != nil {
		return nil, nil, err
	}

	if verbose {
		log.Printf("Connected to %s as %s\n", authTest.URL, authTest.User)
	}
	return client, authTest, nil
}

func main() {
	app := cli.NewApp()
	app.Name = "slack-status"
	app.Usage = "Set your Slack status"

	app.Flags = []cli.Flag{
		cli.StringFlag{
			Name:   "token",
			EnvVar: "SLACK_TOKEN",
			Usage:  "Slack authentication token",
		},
		cli.BoolFlag{
			Name:  "verbose",
			Usage: "Enable Slack API debug logging",
		},
	}

	app.Commands = []cli.Command{
		{
			Name:  "set",
			Usage: "Set Slack status",
			Flags: []cli.Flag{
				cli.StringFlag{
					Name:  "text",
					Usage: "Status text, for example 'Lunch'",
				},
				cli.StringFlag{
					Name:  "emoji",
					Usage: "Status emoji, for example :sandwich:",
				},
				cli.StringFlag{
					Name:  "duration",
					Usage: "Automatically clear status after duration has passed, for example 30m.",
				},
			},
			Action: func(c *cli.Context) error {
				client, authResponse, err := connect(c)
				if err != nil {
					return fmt.Errorf("unable to connect: %v", err)
				}

				statusText := c.String("text")
				if statusText == "" && c.NArg() > 0 {
					statusText = strings.Join(c.Args(), " ")
				}

				statusEmoji := c.String("emoji")

				var expiration int64 = 0
				durationArg := c.String("duration")
				if durationArg != "" {
					duration, err := time.ParseDuration(durationArg)
					if err != nil {
						log.Fatalf("Unable to parse duration: %v", err)
					}
					expiration = time.Now().Add(duration).Unix()
				}

				if c.GlobalBool("verbose") {
					msg := fmt.Sprintf("Setting status to '%+v' with emoji '%+v'", statusText, statusEmoji)
					if expiration > 0 {
						msg += fmt.Sprintf(" until %v", time.Unix(expiration, 0))
					}
					log.Println(msg)
				}

				err = client.SetUserCustomStatusWithUser(authResponse.UserID, statusText, statusEmoji, expiration)
				if err != nil {
					return fmt.Errorf("unable to set status: %v", err)
				}

				return nil
			},
		},
		{
			Name:  "clear",
			Usage: "Clear Slack status",
			Action: func(c *cli.Context) error {
				client, authResponse, err := connect(c)
				if err != nil {
					return fmt.Errorf("unable to connect: %v", err)
				}

				err = client.SetUserCustomStatusWithUser(authResponse.UserID, "", "", 0)
				if err != nil {
					return fmt.Errorf("unable to set status: %v", err)
				}

				return nil
			},
		},
	}

	if err := app.Run(os.Args); err != nil {
		panic(err)
	}
}
