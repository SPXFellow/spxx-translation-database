import jira from 'jira.js'
import fs from 'fs'

const Client = jira.Version2Client

const jql = 'project = MC AND resolved > lastRun AND resolution = Fixed AND fixVersion in unreleasedVersions()'
const mojira = new Client({
  host: 'https://bugs.mojang.com',
})
const lastRun = fs.readFileSync('./lastRun').toString()
fs.writeFileSync('./lastRun', new Buffer.from(Date.now().toString()))

// https://github.com/mojira/mojira-discord-bot/blob/master/src/tasks/FilterFeedTask.ts
const searchResults = await mojira.issueSearch.searchForIssuesUsingJql({
  jql: jql.replace('lastRun', lastRun),
  fields: ['key', 'summary'],
})

console.log(searchResults)

if ( !searchResults.issues ) {
  console.log('No new issues found.')
  process.exit(0) 
}

const tr = JSON.parse(fs.readFileSync('./en.json').toString())
const added = {}
for (const i of searchResults.issues) {
  added[i.key] = i.fields.summary
}
const newTr = Object.assign(added, tr)
console.log(newTr)
fs.writeFileSync('./en.json', JSON.stringify(newTr))
