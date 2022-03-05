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
  fields: ['key', 'summary', 'description'],
})

console.log(searchResults)

if ( !searchResults.issues || searchResults.issues.length === 0 ) {
  console.log('No new issues found.')
  console.log('::set-output name=new-issue::no')
  process.exit(0)
}

const tr = JSON.parse(fs.readFileSync('./en.json').toString())
const added = {}
for (const i of searchResults.issues) {
  added[i.key] = {
    message: i.fields.summary,
    description: i.fields.description,
  }
}
const newTr = Object.assign(added, tr)
console.log(newTr)
fs.writeFileSync('./en.json', JSON.stringify(newTr))
